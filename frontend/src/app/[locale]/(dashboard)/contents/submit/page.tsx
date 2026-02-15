import ContentSubmitForm from '@/components/content/ContentSubmitForm';
import { useTranslations } from 'next-intl';

export default function SubmitContentPage() {
  const t = useTranslations('Contents.Submit');

  return (
    <div className="max-w-3xl mx-auto">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-foreground sm:text-3xl sm:truncate">
            {t('title')}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {t('description')}
          </p>
        </div>
      </div>
      <ContentSubmitForm />
    </div>
  );
}
