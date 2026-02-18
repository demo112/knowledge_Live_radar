# Guidelines
1. depth_balance_score: 评估层级深度是否合理（建议3-5层），各层级节点数量是否均衡
2. coverage_score: 评估内容覆盖率，是否有空节点或内容稀疏节点
3. activity_score: 评估节点活跃度，是否有长期未更新的僵尸节点
4. suggestions 数量建议 3-5 条，按优先级排序
5. confidence 表示建议的确定性程度，0.8 以上为高置信度
6. reason 必须具体说明为什么需要这个操作
7. 对于缺少描述的节点（特别是层级0或1），建议 `update_node`，并强制在 params.description 中生成一段基于节点名称、父节点和兄弟节点上下文的简短描述（50字以内）。描述应说明该节点负责收纳哪类知识。
8. 对于内容严重缺失的关键节点，建议 `add_source`，并在 params 中提供：
   - name: 推荐的源名称（如“{NodeName} 官方文档”）
   - description: 说明为什么要添加这个源
   - type: 推荐的类型（web/rss）
   - url: 设为 "http://pending-configuration"（占位符）
