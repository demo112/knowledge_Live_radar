---
name: attendance-domain
description: "考勤业务、考勤规则、打卡、排班、班次、考勤知识、时间段、考勤系统"
triggers:
  - 考勤
  - 打卡
  - 排班
  - 班次
  - 时间段
---

# 考勤系统业务领域

本 Skill 提供考勤系统的业务领域知识，帮助 Agent 理解业务背景、数据模型和业务规则。

## 激活方式

### 触发场景

以下场景自动加载本 Skill：

- 开发考勤相关功能时
- 需要理解考勤业务规则时
- 设计考勤数据模型时
- 处理考勤异常逻辑时

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | 考勤、打卡、排班、班次、时间段 |
| 功能类 | 签到、签退、补签、请假、出差 |
| 统计类 | 考勤汇总、考勤明细、考勤报表 |
| 异常类 | 迟到、早退、缺勤、旷工 |

---

## 系统概述

三端考勤管理系统：
- **Server**：后端服务
- **Web**：管理端
- **App**：移动打卡端

---

## 核心概念

### 用户 vs 人员

| 概念 | 定义 | 职责 | 关系 |
|------|------|------|------|
| **用户 (User)** | 登录系统的账号主体 | 身份认证、权限控制 | 一个用户必须关联一个人员 |
| **人员 (Employee)** | 企业内的自然人 | 打卡、排班、请假、考勤统计 | 一个人员不一定有用户账号 |

> 关键区分：人员是考勤主体，用户是登录主体。普通工人可能只有人员档案没有系统账号。

### 考勤时间概念

| 概念 | 说明 |
|------|------|
| **考勤日** | 逻辑上的工作日，不等于自然日 |
| **考勤日切换点** | 默认凌晨5点，该时间前的打卡归属前一考勤日 |
| **跨天打卡** | 夜班场景，如凌晨3点打卡算前一天 |

### 时间段类型

| 类型 | 计算方式 | 适用场景 |
|------|----------|----------|
| **普通时间段** | 固定上下班时间 | 标准工时制 |
| **弹性时间段** | 首尾打卡 或 两两累积 | 弹性工作制 |

---

## 数据模型

### 模块归属

| 模块 | 负责人 | 表前缀 |
|------|--------|--------|
| 用户/组织 | sasuke | `user_`, `dept_` |
| 考勤 | naruto | `att_` |

### 核心表结构

#### 用户/组织模块

```
employees (人员表)
├── id, employee_no, name, phone, email
├── dept_id → departments
└── status: active/inactive/resigned

users (用户表)
├── id, username, password_hash
├── employee_id → employees (唯一)
└── status: active/disabled

departments (部门表)
├── id, name, parent_id (自引用)
└── sort_order
```

#### 考勤模块

```
att_time_periods (时间段表)
├── 普通时间段：work_start, work_end, check_in/out 时间窗口
├── 弹性时间段：flex_calc_method, flex_daily_hours
└── 异常规则：late_rule, early_leave_rule (JSON)

att_shifts (班次表)
├── name, cycle_days (默认7天)
└── att_shift_periods 关联多个时间段

att_schedules (排班表)
├── employee_id, shift_id
└── start_date, end_date (有效期)

att_clock_records (原始打卡记录)
├── employee_id, clock_time
└── clock_type: app/web

att_daily_records (每日考勤记录)
├── employee_id, work_date, shift_id, period_id
├── check_in_time, check_out_time
├── status: normal/late/early_leave/absent/leave
└── actual_hours, effective_hours, late_minutes...

att_corrections (补签记录)
├── employee_id, daily_record_id
├── type: check_in/check_out
└── correction_time, operator_id

att_leaves (请假/出差记录)
├── employee_id, type, start_time, end_time
└── status: pending/approved/rejected
```

---

## 业务规则

### 考勤状态判定

| 状态 | 判定条件 |
|------|----------|
| normal | 正常签到签退 |
| late | 签到时间 > 上班时间 + 容忍时间 |
| early_leave | 签退时间 < 下班时间 - 容忍时间 |
| absent | 未签到或未签退 |
| leave | 有审批通过的请假记录 |

### 时长计算

| 时长类型 | 计算方式 |
|----------|----------|
| 实际出勤时长 | 签退时间 - 签到时间 |
| 有效出勤时长 | 实际时长 - 迟到时长 - 早退时长 |
| 缺勤时长 | 应出勤时长 - 有效出勤时长 |

### 数据保留策略

| 表 | 保留期限 |
|------|----------|
| att_clock_records | 2年 |
| att_daily_records | 2年 |
| 其他 | 永久 |

---

## 功能规格索引

| 规格编号 | 功能 | 负责人 |
|----------|------|--------|
| UA1 | 用户管理 | sasuke |
| UA2 | 人员管理 | sasuke |
| UA3 | 部门管理 | sasuke |
| SW62 | 考勤制度 | naruto |
| SW63 | 时间段设置 | naruto |
| SW64 | 班次管理 | naruto |
| SW65 | 排班管理 | naruto |
| SW66 | 补签处理 | naruto |
| SW67 | 请假/出差 | naruto |
| SW68 | 补签记录 | naruto |
| SW69 | 原始考勤数据 | naruto |
| SW70 | 考勤汇总 | sasuke |
| SW71 | 考勤明细 | sasuke |
| SW72 | 统计报表 | sasuke |

---

## 模块边界

### sasuke 负责

- 用户管理：账号CRUD、认证、权限
- 人员管理：人员档案（入职、离职、信息维护）
- 组织架构：部门树管理
- 考勤统计：SW70、SW71、SW72

### naruto 负责

- 考勤制度：SW62
- 时间段/班次/排班：SW63、SW64、SW65
- 考勤处理：SW66、SW67、SW68
- 原始考勤数据：SW69

---

## 开发优先级

| 优先级 | 内容 | 目标 |
|--------|------|------|
| P0 | 用户登录 + 基础打卡 | 最小可用 |
| P1 | 排班 + 考勤处理 + 基础报表 | 核心功能 |
| P2 | 完整报表 | 完整功能 |

---

## 引用资料

详细规格请参考：
- #[[file:attendance-system/docs/requirements.md]]
- #[[file:attendance-system/docs/database-design.md]]
- #[[file:attendance-system/docs/project-roadmap.md]]