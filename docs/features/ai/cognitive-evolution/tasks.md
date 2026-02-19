# Tasks: Iteration 3 - Cognitive Evolution

## Backend

- [x] **数据模型升级**
  - [x] Update `Approval` model (source_content_id, snapshot fields).
  - [x] Create `Concept` & `ConceptSynonym` models.
  - [x] Migration script (Alembic).

- [x] **输入处理服务 (Input Processing)**
  - [x] `InputProcessor` service (Text/URL/File).
  - [x] Basic File parsing (Text extraction).
  - [x] OCR Integration (PDF/Image support).

- [x] **AI 核心服务 (Cognitive Engine)**
  - [x] `ConceptExtractor`: Prompt engineering for extraction.
  - [x] `ConceptMatcher`: Synonym-based matching logic.
  - [x] `ProposalGenerator`: Create `create_node` / `link_content` proposals.
  - [x] `ProposalGenerator`: Implement auto-classification & cluster discovery.
  - [x] Mock AI Service for testing.

- [x] **同义词管理 (Synonyms)**
  - [x] `SynonymService` CRUD.
  - [x] API Endpoints (`/api/v1/synonyms`).

- [x] **审批与回滚 (Approval & Rollback)**
  - [x] `DecisionExecutor` implementation.
  - [x] `SnapshotService` (Backup/Restore).
  - [x] Rollback endpoint implementation.
  - [x] Integration Tests (`test_approval_flow`, `test_rollback_flow`).

## Frontend

- [x] **贡献提交页面 (Contributions)**
  - [x] Layout & Tabs (Text/Link/File).
  - [x] Integration with submission APIs.
  - [x] Submission history list.
  - [x] Analysis result detail view.

- [x] **审批中心 (Approval)**
  - [x] Pending list view.
  - [x] Approve/Reject actions.
  - [x] Execution & Rollback UI.
  - [x] Diff/Impact visualization.

- [x] **同义词管理 (Synonyms)**
  - [x] List page.
  - [x] Add/Edit modal.
  - [x] Integration with Synonyms API.

## Integration & QA

- [x] **End-to-End Validation**
  - [x] Backend Integration Tests (Passed).
  - [x] Frontend E2E Tests (Playwright).

- [x] **Documentation**
  - [x] Design Doc.
  - [x] API Spec Update (Updated in Design Doc).
