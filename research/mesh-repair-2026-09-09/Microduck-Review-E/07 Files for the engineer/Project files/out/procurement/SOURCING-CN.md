# 采购单 · PROCUREMENT — ready-to-send, Shenzhen-local

*For a Microduck build at Black Ark, Room 405, 电子科技大厦, 华强北. Quantities are per robot,
from `out/bom-priced-rung6.csv`. **Nothing here has been ordered.** Paste the Chinese blocks
straight into 1688 / 淘宝 / WeChat.*

**Delivery address, in the form Chinese couriers expect:**

```
广东省深圳市福田区华强北 深南中路2070号 电子科技大厦 405室
收件人：Leif Rydenfalk    电话：<你的手机号>
```

---

## A · THE DECISION THAT COMES FIRST — servos

You have two routes and they differ by ~US$200 and by whether you import at all.

| | Dynamixel XL330-M288-T | Feetech STS3215 7.4V (19 kg·cm) |
|---|---|---|
| qty | 15 | 14 (ancestor's count) |
| unit | **$23.90** intl / $27.49 US | **≈¥100 / €14** |
| total | **$358.50** | **≈¥1,400 / €196** |
| origin | ROBOTIS, **Korea — must import** | **飞特 Feetech, Shenzhen — local** |
| fits current CAD? | **yes, modelled to it** | **no — pockets must be re-modelled** |

**Feetech (飞特) is a Shenzhen company.** Buying STS3215 removes your only real import *and*
cuts the dominant cost line by ~60%. It costs you re-modelling `upper-leg-*`, `yaw2roll`,
`motor-support` and the ankle group, plus a re-run of the MuJoCo walk test (rung 3) to confirm
it still walks. **Decide this before spending anything.**

### 询价 message — Feetech STS3215 (paste to 1688 / 淘宝 / 飞特官方店)
```
你好，我在深圳华强北做一个双足机器人项目，需要采购舵机：

型号：STS3215  7.4V  19kg.cm  串行总线舵机
数量：16 个（14 个装机 + 2 个备用）
需要：舵机 + 配套连接线 + 舵机支架/舵盘（如有套装请推荐）

请问：
1. 单价和 16 个的总价是多少？可以开发票吗？
2. 现货吗？深圳市内可以自提或当天送达吗？
3. 有没有配套的总线控制板（例如 Waveshare Bus Servo Adapter）一起报价？
4. 提供 STEP 或 DXF 的外形尺寸图吗？我需要按尺寸建模安装位。

收货地址：深圳市福田区华强北深南中路2070号 电子科技大厦 405室
谢谢！
```

### If you stay with Dynamixel instead
ROBOTIS XL330-M288-T ×15 + Robot Cable-X3P 180 mm 10-pack ×2. Korea-origin; a Chinese
distributor or Taobao agent avoids paying an overseas merchant directly — relevant because your
Alipay is blocked for cross-border. **询价:**
```
你好，需要采购 ROBOTIS Dynamixel XL330-M288-T 舵机 15 个，
以及 Robot Cable-X3P 180mm 线材 2 包（每包10条）。
请问有现货吗？含税单价、总价和交期各是多少？可以开发票吗？
收货地址：深圳市福田区华强北深南中路2070号 电子科技大厦 405室
```

---

## B · WALK DOWNSTAIRS — 华强北, same day, cash or Alipay in RMB

Take this list on your phone. Everything here is in the markets within ~10 minutes.

| # | item | qty | 中文名称 / 搜索词 | spec to state |
|---|---|---|---|---|
| 1 | ball bearing MR1622-ZZ | **11** | 微型深沟球轴承 **MR1622-ZZ** | 22×16×4 mm，带铁盖 |
| 2 | ball bearing MR6700 open | **3** | 微型深沟球轴承 **MR6700** 开式 | 15×10×3 mm |
| 3 | M2 socket-head screws | ~80 | **M2 内六角圆柱头螺丝 黑色 12.9级** | 长度 4 / 6 / 8 / 12 mm 各若干 |
| 4 | M2 nuts | ~20 | M2 六角螺母 | |
| 5 | M2.5×6 socket head | few | M2.5×6 内六角 | |
| 6 | M2 heat-set inserts | **60** | **M2 热熔螺母 / 预埋铜螺母** | 外径3.2–4.0 长度3–4mm，滚花 |
| 7 | speaker | 1 | **小型喇叭 2W 8欧** | 35×25×7 mm 方形 — **量一下再买，BOM 里这项是 CANNOT DETERMINE** |
| 8 | microphone | ≥1 | 驻极体麦克风 / MEMS 麦克风模块 | |
| 9 | IMX219 camera + M12 lens | 1 | **IMX219 摄像头模组 M12 接口** + **M12 广角镜头** | 22-pin MIPI CSI 排线一起买 |
| 10 | 22-pin MIPI CSI ribbon | 1 | 22P MIPI CSI 排线 | 长度按装配定，先买 100/150/200 mm 各一 |
| 11 | NP-F550 battery + charger | 1+1 | **索尼 NP-F550 电池 2600mAh** + 双充 | 2S 锂电 |
| 12 | PLA filament | 1 kg | **Bambu PLA Basic** 或同级 | 1.26 g/cm³ — 每台机器人 218 g |
| 13 | TPU filament | 0.5 kg | **TPU 85A** | 1.18 g/cm³ — 每台 26 g |
| 14 | JST / Dupont / heat shrink | — | JST-XH / PH 连接器、杜邦线、热缩管 | |

> **Two of these close open questions by being bought.** The speaker and the microphone are
> `CANNOT DETERMINE` in `docs/BOM.md`. Buy them, measure them, and write the real part into the
> BOM — that is two unknowns removed for about ¥30.

### 华强北 walk-in phrase, if you want it in one line
```
你好，我要买微型轴承 MR1622-ZZ 十一个、MR6700 三个，
还有 M2 内六角螺丝（4/6/8/12mm）、M2 热熔螺母 60 个。有现货吗？
```

---

## C · SHENZHEN, NEXT-DAY — LCSC (立创商城) and JLCPCB (嘉立创)

**LCSC — chips for the Robot HAT.** Only one part number is verified in your own BOM; the rest
must be searched by MPN, and I have **not** invented codes for them:

| MPN | qty | LCSC code | status |
|---|---|---|---|
| TLV320AIC3104IRHBR | 1 | **C181753** | **verified — priced $2.25 in `out/bom-priced-rung6.csv`** |
| LSM6DSV16X | 1 | — | search by MPN on lcsc.com |
| BMI088 | 1 | — | search by MPN (optional per `[C-elec]`) |
| VL53L8CX | 1 | — | search by MPN |
| passives (0402), pull-ups 10 kΩ ×2 | — | — | from the P1 schematic, which does not exist yet |

`out/procurement/lcsc-bom.csv` is uploadable to LCSC's BOM tool as-is.

**JLCPCB — the three PCBs.** Fab + assembly in days, *once designs exist*. They do not.
See `BUILD-PACK.md` §2.1. There is nothing to order here today.

---

## D · WHAT I CANNOT DO, PLAINLY

I have a shell, files and web fetch. **I have no browser control, no email, no messaging, and no
payment method.** I cannot place an order, cannot open a supplier chat, and will not buy on your
behalf. "You're the voice" is the part I *can* do, and it is above: the messages are written and
addressed — you paste and send.

**The one thing that would change this:** wire **Playwright MCP** into this session and I get a
real browser I can drive — I could then fill carts, compare suppliers and take it to the
checkout page. **I would still stop at payment** and hand it to you.
