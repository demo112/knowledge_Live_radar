import ContentSubmitForm from '@/components/content/ContentSubmitForm';

export default function SubmitContentPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-foreground sm:text-3xl sm:truncate">
            提交内容
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            提交文章、文档或文本进行分析。
          </p>
        </div>
      </div>
      <ContentSubmitForm />
    </div>
  );
}
