# Daikin DS-AIR Custom Component For Home Assistant

## 关于本集成 / About this integration

| 项目 | 说明 |
|------|------|
| **原作者 / Original author** | [mypal](https://github.com/mypal/ha-dsair)（wangsc100@gmail.com）。原始实现与版权归其所有，感谢 mypal 的原创工作。 |
| **修改者 / Maintainer** | [bobbyleu](https://github.com/bobbyleu/ha-dsair)（bobbyleu@163.com）。本仓库为其维护的分叉版本，并非从零创作。 |
| **修改基线 / Based on** | mypal 上游 `2.3.0-alpha.1`（分叉点），当前分叉版本 `2.3.0-alpha.1-bobbyleu.2`。 |
| **修改了什么 / Changes** | ① Home Assistant 新版本兼容性修复（弃用告警、实体刷新线程安全、启动即轮询状态）；② 新增浴室空调换气扇独立 `fan` 实体；③ 新增金制空气云端电量统计与原生能源面板集成；④ 支持垂直/水平风向独立控制及 Emoji 图标；⑤ 修复小新风（Small VAM）经 HomeKit Bridge 自动化只调风量、无法开机的问题：设风速、预设模式时显式下发开机命令，风速归零时下发关机命令；⑥ 新增 HomeKit 专用新风实体（`*_homekit`），在苹果家庭中呈现为「开关 + 风速 + 自动」单一配件，不再为每个模式生成独立开关；同时修复通过「模式/风量」select 实体在关机状态下切换时不开机的问题。 |

> **版本命名 / Versioning**：本仓库沿用 `<上游版本>-bobbyleu.<N>` 命名方案（与 rinnai_smart 一致）。`<上游版本>` 是本分叉所基于的 mypal 上游版本（当前为 `2.3.0-alpha.1`），`<N>` 是本分叉自身的修订序号。例如 `2.3.0-alpha.1-bobbyleu.2` 表示「基于上游 2.3.0-alpha.1 的第 2 次修订」。
>
> This integration was originally created by [mypal](https://github.com/mypal/ha-dsair) and is currently forked and maintained by [bobbyleu](https://github.com/bobbyleu/ha-dsair), based on upstream `2.3.0-alpha.1`. This fork is not an original work; it focuses on compatibility fixes for newer Home Assistant versions, bug fixes, and the additions listed above.

此项目是Home Assistant平台[DS-AIR](https://www.daikin-china.com.cn/newha/products/4/19/DS-AIR/)以及[金制空气](https://www.daikin-china.com.cn/newha/products/4/19/jzkq/)自定义组件的实现。

支持的网关设备型号为 DTA117B611、DTA117C611，其他网关的支持情况未知。（DTA117D611 可直接选择 DTA117C611）。同时支持直接云端对接“金制空气”账号，自动统计并同步每日电量消耗。

# 支持功能与设备

* 空调设备控制（制冷、制热、除湿、送风、风速、风向）
* 空气质量传感器（温度、湿度、PM2.5、CO2、TVOC、VOC、甲醛）
* 新风系统联动
* 浴室空调换气扇（独立 fan 实体，支持低档 50% / 高档 100% 独立控制）
* **电量消耗统计与原生能源面板集成**：
  * **日常监控（双实体）**：
    * **昨日用电**（`yesterday_power`，kWh）：展示前一日的用电量，方便日常卡片查看与对比。
    * **当月累计用电**（`month_power`，kWh，`state_class: total_increasing`）：展示当月累计用电、电费单价、当月预估电费及每日用电明细列表。可直接添加至 Home Assistant 原生【能源面板】中！
  * **定时自动同步**：每天清晨 05:00 自动拉取前一日电量数据并同步更新至传感器状态，同时自动将当月每日历史数据导入 HA 长期统计库（LTS）。
  * **历史查询与长期统计回溯服务 (`ds_air.get_power_data`)**：
    * 提供 `ds_air.get_power_data` 动作/服务，输入年份和月份（如 2026 年 10 月）即可秒级返回该月任意天电量明细（支持自动化与服务响应）。
    * 支持一键将历史任意月份的日电量数据直接回溯导入至 HA 长期统计库（LTS），让原生【能源面板】的历史每日、每月柱状图直接可用！


# 不支持设备

* 睡眠传感器
* 晴天轮
* 转角卫士
* 金制家中用防护组件
* 显示屏(黑奢系列)

# HomeKit 单配件新风

大金新风的 5 个模式（内循环/热交换/自动/防污染/排异味）如果直接接入 HomeKit Bridge，桥接层会为每个模式生成一个独立开关，苹果家庭里会出现 5 个零散开关。为此本版本额外创建一个 HomeKit 专用实体：

| 实体 | 用途 | 模式 |
|------|------|------|
| `fan.新风_<房间>_开关`（原实体） | HA 界面使用，保持不变 | 5 个模式全部保留 |
| `fan.新风_<房间>_homekit_*`（新实体） | 只给 HomeKit 使用 | 仅 1 个「自动」模式 |

HA 的 HomeKit 桥接层规则是：当风扇只有 1 个 preset 模式时，把它渲染成**一个配件**（开关 + 风速滑块 + 内嵌「自动」按钮），而不再为每个模式生成独立开关。新实体就利用这一规则。「自动」按钮打开时切换到自动模式并开机；关闭时退出自动模式、按当前风速继续运行。

新实体与原实体属于同一个 HA 设备，不会在设备页重复出现。为了不影响 HA 界面，建议将其在 HA 前端隐藏（设置 → 设备与服务 → 实体 → 搜索 `homekit` → 隐藏）；隐藏不影响 HomeKit 桥接。

## HomeKit Bridge 配置

在 HA 的 HomeKit Bridge 集成配置里，需要**包含新实体、排除原实体**，二选一操作：

- **方式一（推荐，只桥接新风时）**：HomeKit Bridge → 配置 → 「包含」选项卡，只勾选 `fan.新风_<房间>_homekit_*`，不勾选原来的 `fan.新风_<房间>_开关`。
- **方式二（已在桥接其它设备）**：HomeKit Bridge → 配置 → 「排除」选项卡，加入原来的 `fan.新风_<房间>_开关`，并确保新实体在包含列表中。

修改后重载 HomeKit Bridge，苹果家庭中原来的 5 个模式开关会消失，只留下一个「新风」配件（开关 + 风速 + 自动）。HA 内的原实体功能不受影响。

# 浴室空调换气扇

本分支新增浴室空调的换气扇支持，以独立的 `fan` 实体暴露，具备以下特性：

- 两个档位：低（50%）/ 高（100%）
- 换气功能完全独立于空调，开关互不影响
- APP/弱电面板操作后 HA 状态实时同步
- 新用户配置时自动发现

## 使用

安装后在 HA 中会出现 `fan.yu_shi_kong_diao_kong_diao_pai_feng_shan` 实体，支持：
- `fan.turn_on` — 开启换气（默认低档）
- `fan.turn_off` — 关闭换气
- `fan.set_percentage(50)` — 低档
- `fan.set_percentage(100)` — 高档

## 修复的问题

| 问题 | 说明 |
|------|------|
| breathe 命令未编码 | `param.py` 缺少 breathe 字段编码，导致换气控制命令静默丢弃 |
| 开换气连带开空调 | `fan.py` 的 `set_percentage`/`turn_on` 会自动设置空调开关 |
| 关换气连带关空调 | `fan.py` 的 `turn_off` 会设置空调关闭 |
| HA 状态不同步 | `service.py` 的 `poll_status` 未查询 BATHROOM 设备 |
| 新用户发现不了 | `decoder.py` 缺少 `set_device` 调用，浴室空调设备未注册 |
| 风速选项过多 | `climate.py` 未根据 `EnumFanVolume` 能力过滤可用风速 |
| 集成僵尸化 | `service.py` socket 关闭竞态导致线程崩溃 (#112) |

# 接入方法

## 安装
- 方法一：将项目 `ds_air` 目录直接拷贝到 `/config/custom_components/` 目录下

- 方法二：点击此按钮添加 HACS 自定义存储库 

  [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bobbyleu&repository=ha-dsair&category=integration)

  然后点击右下角 DOWNLOAD 安装

## 配置 
    
- 方法一：在`配置-集成-添加集成`中选择`DS-AIR`

- 方法二：直接点击此按钮 [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ds_air)

在配置第一步可选择配置类型：
1. **配置网关**：填入局域网网关IP、端口号、设备型号等，完成局域网空调与传感器接入。
2. **配置电量统计**：输入大金“金制空气”手机号和密码登录，并选择要统计的家庭，即可自动创建电量传感器并按日同步。

# 开发过程

本组件开发过程可在[blog](https://www.mypal.wang/blog/lun-yi-ci-jia-yong-kong-diao-jie-ru-hazhe-teng-jing-li/)查看
