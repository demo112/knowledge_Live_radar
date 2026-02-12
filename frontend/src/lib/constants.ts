export const CHANGE_STATUS_MAP: Record<string, string> = {
  executed: '已执行',
  rolled_back: '已回滚',
  failed: '失败',
  pending: '待处理',
  approved: '已批准',
  rejected: '已拒绝',
};

export const CHANGE_TYPE_MAP: Record<string, string> = {
  create_node: '创建节点',
  update_node: '更新节点',
  delete_node: '删除节点',
  add_source: '添加信息源',
  update_source: '更新信息源',
  delete_source: '删除信息源',
  create_pyramid: '创建金字塔',
  delete_pyramid: '删除金字塔',
  // Add others as needed
};

export const RISK_LEVEL_MAP: Record<string, string> = {
  low: '低',
  medium: '中',
  high: '高',
  critical: '严重',
};
