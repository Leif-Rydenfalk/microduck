"""Regression: exported 3MF retains manifold adjacency and oriented surfaces."""
import collections
import unittest
import xml.etree.ElementTree as ET
from indexed_3mf import mesh_xml

class ExportTests(unittest.TestCase):
    def test_closed_tetrahedron_retains_edge_adjacency(self):
        v=[(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
        faces=[(0,2,1),(0,1,3),(0,3,2),(1,2,3)]
        soup=[v[i] for face in faces for i in face]
        xml=ET.fromstring(mesh_xml(soup))
        points=[tuple(float(p.get(k)) for k in ('x','y','z')) for p in xml.find('vertices')]
        triangles=[tuple(int(p.get(k)) for k in ('v1','v2','v3')) for p in xml.find('triangles')]
        self.assertEqual(len(points),4)
        edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in triangles for i in range(3))
        self.assertEqual(set(edges.values()),{2})
        self.assertEqual([points[i] for f in triangles for i in f],soup)

    def test_output_precision_and_signed_zero_share_vertex(self):
        xml=ET.fromstring(mesh_xml([(0.,0,0),(-0.,0,0),(.00001,0,0)]))
        self.assertEqual(len(xml.find('vertices')),1)

    def test_incomplete_face_refused(self):
        with self.assertRaises(ValueError):mesh_xml([(0,0,0)])

if __name__=='__main__':unittest.main()
