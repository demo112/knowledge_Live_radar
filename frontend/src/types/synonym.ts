export interface Synonym {
    id: string;
    canonical_term: string;
    synonym: string;
    source: string;
    confidence: number;
    is_active: boolean;
    usage_count: number;
    created_at: string;
    updated_at: string;
}

export interface SynonymCreate {
    canonical_term: string;
    synonym: string;
    source?: string;
    confidence?: number;
}
