# 考勤系统项目概述

## 项目目标

三端考勤管理系统：Server（后端）、Web（管理端）、App（移动打卡端）

## 技术栈

| 模块 | 技术 |
|------|------|
| Server | Node.js + Express + TypeScript + Prisma |
| Web | React + TypeScript + Vite |
| App | React Native + Expo + TypeScript |

## 分工

| 负责人 | 模块 | 规格 |
|--------|------|------|
| sasuke | 用户/人员/部门/统计 | SW70-72 |
| naruto | 考勤核心 | SW62-69 |

## 关键文档

| 文档 | 路径 |
|------|------|
| 需求规格 | docs/requirements.md |
| 数据库设计 | docs/database-design.md |
| API 契约 | docs/api-contract.md |
| 功能文档 | docs/features/{SPEC_ID}/ |
| Prisma Schema | packages/server/prisma/schema.prisma |

## AI 行为规则

### 意图识别

| 用户话题 | 推荐能力 |
|----------|----------|
| "想做"、"需要" | 需求分析 |
| "怎么做"、"方案" | 技术设计 |
| "报错"、"问题" | 问题修复 |
| "做完了" | 验证/提交/文档 |
