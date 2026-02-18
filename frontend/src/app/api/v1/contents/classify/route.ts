import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000/api/v1';

export const maxDuration = 60;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 55000);
    
    const response = await fetch(`${BACKEND_URL}/contents/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { success: false, error: errorData.detail || 'Classification failed' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Classify API error:', error);
    
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { success: false, error: 'Request timeout' },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
