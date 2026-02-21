import api from '@/lib/api';

export enum IntentType {
  LEARN = "learn",
  RESEARCH = "research",
  TRACK = "track",
  CREATE = "create",
  GENERAL = "general"
}

export enum ActionType {
  CREATE_NODE = "create_node",
  CREATE_CLUSTER = "create_cluster",
  SEARCH_CONTENT = "search_content",
  GENERATE_REPORT = "generate_report",
  SUBSCRIBE_TOPIC = "subscribe_topic"
}

export interface Action {
  type: ActionType;
  description: string;
  parameters: Record<string, any>;
  priority: number;
}

export interface IntentParseResult {
  original_text: string;
  intent_type: IntentType;
  primary_topic: string;
  sub_topics: string[];
  goal?: string;
  parameters: Record<string, any>;
  confidence: number;
}

export interface IntentResponse {
  id: string;
  parsed_intent: IntentParseResult;
  suggested_actions: Action[];
}

export const intentApi = {
  parse: async (text: string) => {
    const response = await api.post('/intents/parse', { text });
    return response.data;
  },

  process: async (text: string) => {
    const response = await api.post('/intents/process', { text });
    return response.data;
  },
};
