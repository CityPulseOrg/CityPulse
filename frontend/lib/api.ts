// Use internal Docker network URL for server-side requests, public URL for client-side
const getApiBase = () => {
  if (typeof window === 'undefined') {
    // Server-side: use container-to-container communication
    return process.env.API_BASE_URL || 'http://backend:8000';
  }
  // Client-side: use public URL (browser makes requests through host)
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
};

const API_BASE = getApiBase();

export async function createIssue(data: { title?: string; description: string; photos?: File[]; lat?: number; lng?: number }): Promise<import('./types').CreateIssueResponse> {
  const formData = new FormData();
  if (data.title) formData.append('title', data.title);
  formData.append('description', data.description);
  if (data.lat !== undefined) formData.append('latitude', data.lat.toString());
  if (data.lng !== undefined) formData.append('longitude', data.lng.toString());
  if (data.photos) {
    data.photos.forEach((file) => {
      formData.append('issue_images', file);
    });
  }
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    console.error('createIssue failed:', res.status, res.statusText, 'response body:', text,)
    throw new Error(`Failed to create issue: ${res.status}`)
  }
  return res.json();
}

export async function getIssue(id: string): Promise<import('./types').IssueDetails> {
  const res = await fetch(`${API_BASE}/reports/${id}`);
  if (!res.ok) throw new Error('Failed to get issue');
  return res.json();
}

export async function followupIssue(id: string, answers: { [key: string]: string }): Promise<import('./types').IssueDetails> {
  const res = await fetch(`${API_BASE}/reports/${id}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ followup: answers }),
  });
  if (!res.ok) throw new Error('Failed to followup');
  return res.json();
}

export async function updateIssueStatus(id: string, status: string): Promise<void> {
  const res = await fetch(`${API_BASE}/v1/issues/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update status');
}

export async function getIssues(filters?: { status?: string; category?: string; priority?: string }): Promise<import('./types').IssueDetails[]> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.category) params.append('category', filters.category);
  if (filters?.priority) params.append('priority', filters.priority);
  const res = await fetch(`${API_BASE}/v1/issues?${params}`);
  if (!res.ok) throw new Error('Failed to get issues');
  return res.json();
}