#!/usr/bin/env python3
"""Offline SV-01 evidence-package validator. No device, network or write interface."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'spec/servo-capture-contract.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_bytes(base, name):
    """Only regular files inside the supplied package; never /dev, FIFO or URL."""
    path = (base / name).resolve()
    path.relative_to(base.resolve())
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('not a regular file')
    return path.read_bytes()


def timestamp(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).utcoffset() is not None
    except (TypeError, ValueError, AttributeError):
        return False


def validate(path):
    path = Path(path).resolve()
    raw = local_bytes(path.parent, path.name)
    doc = json.loads(raw)
    contract = json.loads(CONTRACT.read_text())
    findings, observations = [], []

    def add(level, code, where, why):
        findings.append(dict(level=level, code=code, where=where, why=why))

    def gap(code, where, why):
        add('CANNOT DETERMINE', code, where, why)

    def bad(code, where, why):
        add('FAIL', code, where, why)

    if not isinstance(doc, dict) or doc.get('schema') != 1:
        raise ValueError('manifest must be an object with schema 1')
    if type(doc.get('synthetic')) is not bool:
        bad('synthetic_flag', 'manifest', 'Explicit synthetic true/false required.')
    if doc.get('synthetic'):
        gap('synthetic', 'manifest', 'Synthetic example: no original hardware evidence.')
    for key in ('operator', 'sample_id', 'original_robot_serial', 'original_robot_revision', 'runtime_build'):
        if not isinstance(doc.get(key), str) or not doc[key].strip():
            gap('provenance_missing', key, 'Record the actual value or leave unresolved; do not infer it.')
    if not timestamp(doc.get('captured_at')):
        gap('timestamp_missing', 'captured_at', 'Timezone-bearing capture timestamp required.')
    for source in contract['sources']:
        if digest(local_bytes(ROOT, source['path'])) != source['sha256']:
            bad('source_changed', source['path'], 'Pinned validation source changed; review contract.')
    plan = json.loads((ROOT / 'spec/test-plan.json').read_text())
    sv = next(t for s in plan['sections'] for t in s.get('tests', []) if t['id'] == 'SV-01')
    required = {int(r['address']) for r in contract['registers']}
    if sv.get('execution_status') != 'IDENTIFICATION_ONLY' or not {r[0] for r in sv['readback']} <= required:
        bad('test_plan_drift', 'SV-01', 'Offline contract no longer covers read-only SV-01.')

    assets = {}
    for i, item in enumerate(doc.get('artifacts', [])):
        where = 'artifacts[%d]' % i
        key = item.get('id')
        if not isinstance(key, str) or not key or key in assets:
            bad('artifact_id', where, 'Missing or duplicate artifact ID.'); continue
        assets[key] = dict(item, data=None)
        try:
            data = local_bytes(path.parent, item['path'])
            if digest(data) != item.get('sha256'):
                bad('artifact_hash', where, 'Supplied bytes disagree with manifest SHA-256.'); continue
            assets[key]['data'] = data
        except (OSError, ValueError, TypeError, KeyError) as exc:
            bad('artifact_unreadable', where, str(exc))
        if not item.get('label'):
            gap('artifact_label', where, 'A file requires a human-readable sample/subject label.')
        if not item.get('sample_id'):
            gap('artifact_sample', where, 'Artifact sample attribution required.')
        elif item['sample_id'] != doc.get('sample_id'):
            bad('artifact_sample_mismatch', where, 'Artifact belongs to a different sample.')

    def asset(key, kind, where):
        item = assets.get(key)
        if not item or item.get('kind') != kind or item['data'] is None:
            gap('artifact_missing', where, 'Need hash-checked %s artifact: %r' % (kind, key))
            return None
        return item

    for role in ('original_robot_identity', 'hat_revision', 'battery_label', 'battery_to_servo_route'):
        if not any(a.get('role') == role and a.get('kind') == 'photo' and a['data'] for a in assets.values()):
            gap('photo_missing', role, 'Labeled original-resolution photo artifact missing.')
    ids = []
    for i, servo in enumerate(doc.get('servos', [])):
        where = 'servos[%d]' % i
        ident = servo.get('observed_id'); ids.append(ident)
        if type(ident) is not int:
            bad('id_type', where, 'Observed ID must be an integer.'); continue
        if not servo.get('joint_label'):
            gap('joint_label', where, 'Observed physical joint label required, not inferred from ID.')
        if not servo.get('servo_serial'):
            gap('servo_serial', where, 'Actual servo serial/marking unavailable; preserve unknown.')
        photos = servo.get('label_photos', [])
        if not photos:
            gap('servo_photo', where, 'Original servo label photo missing.')
        for photo in photos:
            asset(photo, 'photo', where)
        entry = asset(servo.get('snapshot'), 'register_snapshot', where)
        if not entry:
            continue
        try:
            snapshot = json.loads(entry['data'])
            if snapshot.get('observed_id') != ident:
                bad('id_mismatch', where, 'Manifest ID and snapshot ID disagree.')
            if not timestamp(snapshot.get('captured_at')) or not snapshot.get('sample_id'):
                gap('snapshot_provenance', where, 'Snapshot sample ID and timestamp required.')
            if snapshot.get('sample_id') != doc.get('sample_id'):
                bad('sample_mismatch', where, 'Snapshot belongs to another sample.')
            if snapshot.get('read_only') is not True:
                gap('capture_method', where, 'Read-only capture method not attested.')
            if snapshot.get('synthetic') is True and doc.get('synthetic') is not True:
                bad('synthetic_mismatch', where, 'Synthetic snapshot cannot be labeled nonsynthetic in manifest.')
            if 'communication_errors' not in snapshot or snapshot['communication_errors'] != []:
                gap('communication_errors', where, 'Record communication errors explicitly; missing is not error-free.')
            values = {}
            for register in snapshot.get('registers', []):
                address = register.get('address')
                if type(address) is not int or address in values:
                    bad('register_duplicate', where, 'Invalid or duplicate register address.'); continue
                values[address] = register
            missing = required - values.keys()
            if missing:
                gap('register_missing', where, 'Missing addresses %s' % sorted(missing))
            decoded = {}
            # An unknown model must not inherit XL330 address/scale semantics.
            identity = values.get(0, {})
            try:
                model_wire = bytes.fromhex(identity.get('raw_hex', ''))
                known_model = len(model_wire) == 2 and str(int.from_bytes(model_wire, 'little')) in contract['models']
            except (ValueError, TypeError):
                known_model = False
            for rule in contract['registers']:
                address = rule['address']
                if address not in values:
                    continue
                if not known_model and address != 0:
                    continue
                register = values[address]
                try:
                    wire = bytes.fromhex(register['raw_hex'])
                    if len(wire) != rule['bytes']:
                        raise ValueError('wrong byte width')
                    raw_value = int.from_bytes(wire, 'little')
                    if type(register.get('raw')) is not int or register['raw'] != raw_value:
                        raise ValueError('raw integer disagrees with little-endian bytes')
                    value = register['value']
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError('nonfinite or nonnumeric decoded value')
                    if register.get('unit') != rule['unit'] or not math.isclose(value, raw_value * rule['scale'], abs_tol=1e-8):
                        raise ValueError('decoded value/unit disagrees with source encoding')
                    decoded[address] = raw_value
                except (ValueError, TypeError, KeyError) as exc:
                    bad('register_encoding', where + '/%s' % address, str(exc))
            model = contract['models'].get(str(decoded.get(0)))
            observations.append(dict(observed_id=ident, joint_label=servo.get('joint_label'),
                                     decoded_model=model, submitted_snapshot=snapshot))
            if not model:
                gap('model_unknown', where, 'Model unrecognized: requires its exact manufacturer control table and ratings.')
            if model and servo.get('label_model') != model:
                gap('label_model_mismatch', where, 'Label model absent or disagrees with register 0; manual review needed.')
            if 7 in decoded and decoded[7] != ident:
                bad('id_mismatch', where, 'Register 7 disagrees with observed ID.')
            if model and 144 in decoded and not 3.7 <= decoded[144] * 0.1 <= 6.0:
                bad('voltage_rating_conflict', where, 'Submitted telemetry lies outside standard XL330 3.7–6.0 V rating; no instruction to energize or retest.')
            if 63 in decoded and not decoded[63] & 1:
                gap('voltage_shutdown_disabled', where, 'Shutdown input-voltage bit is clear; thresholds/masks do not extend rated voltage.')
            if decoded.get(64, 0) != 0:
                gap('torque_enabled', where, 'Submitted observation says torque enabled; capture conditions require review. No control action issued.')
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            bad('snapshot_format', where, str(exc))
    integer_ids = [n for n in ids if type(n) is int]
    duplicates = sorted(n for n, count in Counter(integer_ids).items() if count > 1)
    if duplicates:
        bad('duplicate_id', 'servos', 'Repeated observed IDs %s; snapshots retained for review.' % duplicates)
    expected = set(contract['expected_runtime_ids'])
    if expected - set(integer_ids):
        gap('missing_id', 'servos', 'Absent runtime IDs %s; never inferred from other devices.' % sorted(expected - set(integer_ids)))
    if set(integer_ids) - expected:
        gap('unexpected_id', 'servos', 'Observed IDs outside pinned runtime %s; original mapping still unconfirmed.' % sorted(set(integer_ids) - expected))
    imu = doc.get('imu', {})
    imu_entry = asset(imu.get('snapshot'), 'imu_snapshot', 'imu')
    if imu.get('observed_id') != contract['imu_id'] or not imu_entry:
        gap('imu_missing', 'imu', 'Separate IMU 200 snapshot required; never apply XL330 register map to bridge.')
    if imu_entry:
        try:
            payload = json.loads(imu_entry['data'])
            if payload.get('observed_id') != imu.get('observed_id') or payload.get('sample_id') != doc.get('sample_id'):
                bad('imu_sample_mismatch', 'imu', 'IMU snapshot ID/sample disagrees with manifest.')
            if not timestamp(payload.get('captured_at')) or 'communication_errors' not in payload:
                gap('imu_provenance', 'imu', 'Separate timestamp and communication-error record required.')
            if payload.get('communication_errors') != []:
                gap('communication_errors', 'imu', 'Record communication errors explicitly; missing is not error-free.')
            if payload.get('read_only') is not True:
                gap('capture_method', 'imu', 'Read-only capture method not attested.')
            if payload.get('synthetic') is True and doc.get('synthetic') is not True:
                bad('synthetic_mismatch', 'imu', 'Synthetic snapshot cannot be labeled nonsynthetic in manifest.')
            if not payload.get('raw_observation') or not payload.get('format_source'):
                gap('imu_format', 'imu', 'Preserve raw observation and exact capture/format source; bridge identity remains unresolved.')
        except (ValueError, TypeError, AttributeError) as exc:
            bad('imu_format', 'imu', str(exc))
    gap('original_identity_unverified', 'package', 'Package integrity does not authenticate original serial/revision, joint mapping, labels, firmware or installed power route; independent review required.')
    gap('electrical_acceptance_unmeasured', 'package', 'No meter/scope/transient test or physical acceptance performed by this offline tool.')
    return dict(schema=1, scope='OFFLINE_EVIDENCE_VALIDATION_ONLY',
                verdict='FAIL' if any(f['level'] == 'FAIL' for f in findings) else 'CANNOT DETERMINE',
                physical_acceptance='CANNOT DETERMINE', original_identity='CANNOT DETERMINE',
                manifest_sha256=digest(raw), contract_sha256=digest(CONTRACT.read_bytes()),
                expected_runtime_ids=sorted(expected), submitted_manifest=doc,
                observations=observations, findings=findings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.manifest)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = dict(verdict='FAIL', scope='OFFLINE_EVIDENCE_VALIDATION_ONLY',
                      physical_acceptance='CANNOT DETERMINE', error=str(exc))
    print(json.dumps(result, indent=2))
    return 1 if result['verdict'] == 'FAIL' else 2


if __name__ == '__main__':
    raise SystemExit(main())
