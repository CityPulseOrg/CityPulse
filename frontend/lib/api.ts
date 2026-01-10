const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function createIssue(data: { description: string; photos?: File[]; lat?: number; lng?: number }): Promise<import('./types').CreateIssueResponse> {
  const formData = new FormData();
  formData.append('description', data.description);
  if (data.lat !== undefined) formData.append('lat', data.lat.toString());
  if (data.lng !== undefined) formData.append('lng', data.lng.toString());
  if (data.photos) {
    data.photos.forEach((file) => {
      formData.append('photos', file);
    });
  }
  const res = await fetch(`${API_BASE}/v1/issues`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to create issue');
  return res.json();
}

export async function getIssue(id: string): Promise<import('./types').IssueDetails> {
  const res = await fetch(`${API_BASE}/v1/issues/${id}`);
  if (!res.ok) throw new Error('Failed to get issue');
  return res.json();
}

export async function followupIssue(id: string, answers: { [key: string]: string }): Promise<import('./types').IssueDetails> {
  const res = await fetch(`${API_BASE}/v1/issues/${id}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
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

export async function getIssues(filters?: { status?: string; category?: string }): Promise<import('./types').IssueDetails[]> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.category) params.append('category', filters.category);
  const res = await fetch(`${API_BASE}/v1/issues?${params}`);
  if (!res.ok) throw new Error('Failed to get issues');
  return res.json();
}