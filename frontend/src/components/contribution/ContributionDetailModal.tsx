import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useTranslations } from 'next-intl';

interface ExtractedConcept {
  name?: string;
  [key: string]: unknown;
}

interface Contribution {
  id: string;
  user_id?: string;
  input_type: string;
  original_input: string;
  status: string;
  extracted_concepts?: (string | ExtractedConcept)[];
  extracted_content?: string;
  created_at: string;
  rejection_reason?: string;
}

interface ContributionDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  contribution: Contribution | null;
}

export default function ContributionDetailModal({
  isOpen,
  onClose,
  contribution,
}: ContributionDetailModalProps) {
  const t = useTranslations('Contributions.detail');
  const tStatus = useTranslations('Contributions.status');

  if (!contribution) return null;

  const getStatusLabel = (status: string) => {
    switch(status) {
      case 'processed': return tStatus('processed');
      case 'rejected': return tStatus('rejected');
      case 'failed': return tStatus('failed');
      default: return tStatus('pending');
    }
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
                <div>
                  <div className="mt-3 text-center sm:mt-0 sm:text-left">
                    <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                      {t('title')}
                    </Dialog.Title>
                    <div className="mt-2 space-y-4">
                      {/* Basic Info */}
                      <div className="bg-gray-50 p-3 rounded-md">
                        <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                          <div className="sm:col-span-1">
                            <dt className="text-sm font-medium text-gray-500">{t('type')}</dt>
                            <dd className="mt-1 text-sm text-gray-900">{contribution.input_type.toUpperCase()}</dd>
                          </div>
                          <div className="sm:col-span-1">
                            <dt className="text-sm font-medium text-gray-500">{t('status')}</dt>
                            <dd className="mt-1 text-sm text-gray-900">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                ${contribution.status === 'processed' ? 'bg-green-100 text-green-800' : 
                                  contribution.status === 'failed' ? 'bg-red-100 text-red-800' : 
                                  'bg-yellow-100 text-yellow-800'}`}>
                                {getStatusLabel(contribution.status)}
                              </span>
                            </dd>
                          </div>
                          <div className="sm:col-span-2">
                            <dt className="text-sm font-medium text-gray-500">{t('original_input')}</dt>
                            <dd className="mt-1 text-sm text-gray-900 break-all">{contribution.original_input}</dd>
                          </div>
                          {contribution.rejection_reason && (
                            <div className="sm:col-span-2">
                              <dt className="text-sm font-medium text-red-500">{t('rejection_reason')}</dt>
                              <dd className="mt-1 text-sm text-red-700">{contribution.rejection_reason}</dd>
                            </div>
                          )}
                        </dl>
                      </div>

                      {/* Extracted Concepts */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{t('extracted_concepts')}</h4>
                        {contribution.extracted_concepts && contribution.extracted_concepts.length > 0 ? (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {contribution.extracted_concepts.map((concept, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center rounded-md bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10"
                              >
                                {typeof concept === 'string' ? concept : concept.name || JSON.stringify(concept)}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="mt-1 text-sm text-gray-500 italic">{t('no_concepts')}</p>
                        )}
                      </div>

                      {/* Extracted Content Preview */}
                      <div>
                         <h4 className="text-sm font-medium text-gray-900">{t('content_preview')}</h4>
                         <div className="mt-2 max-h-40 overflow-y-auto rounded-md bg-gray-50 p-3 text-xs text-gray-700 whitespace-pre-wrap">
                           {contribution.extracted_content || t('no_content')}
                         </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-5 sm:mt-6">
                  <button
                    type="button"
                    className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    onClick={onClose}
                  >
                    {t('close')}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
