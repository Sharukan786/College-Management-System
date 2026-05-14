import { API_BASE } from './apiBase';
export { buildApiUrl } from './apiBase';

async function parseResponse(res, fallbackMessage) {
  const json = await res.json().catch(() => null);
  if (!res.ok || !json?.success) {
    throw new Error(json?.detail || json?.message || fallbackMessage);
  }
  return json;
}

export async function fetchAttendanceSummary(role) {
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  const query = params.toString();
  const res = await fetch(`${API_BASE}/academics/attendance${query ? `?${query}` : ''}`);
  const json = await parseResponse(res, 'Failed to load attendance summary');
  return Array.isArray(json.data) ? json.data : [];
}

export async function fetchAttendanceWeekly(role) {
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  const query = params.toString();
  const res = await fetch(`${API_BASE}/academics/attendance/weekly${query ? `?${query}` : ''}`);
  const json = await parseResponse(res, 'Failed to load weekly attendance');
  return Array.isArray(json.data) ? json.data : [];
}

export async function fetchAttendanceMarkings({ classId, date, hour, studentId } = {}) {
  const params = new URLSearchParams();
  if (classId) params.append('class_id', classId);
  if (date) params.append('date', date);
  if (hour) params.append('hour', hour);
  if (studentId) params.append('student_id', studentId);

  const query = params.toString();
  const res = await fetch(`${API_BASE}/academics/attendance/markings${query ? `?${query}` : ''}`);
  const json = await parseResponse(res, 'Failed to load attendance markings');
  return Array.isArray(json.data) ? json.data : [];
}

export async function saveAttendanceMarking(payload) {
  const res = await fetch(`${API_BASE}/academics/attendance/markings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await parseResponse(res, 'Failed to save attendance marking');
  return json.data;
}

export async function fetchOdRequests({ studentId, status } = {}) {
  const params = new URLSearchParams();
  if (studentId) params.append('student_id', studentId);
  if (status) params.append('status', status);

  const query = params.toString();
  const res = await fetch(`${API_BASE}/academics/attendance/od-requests${query ? `?${query}` : ''}`);
  const json = await parseResponse(res, 'Failed to load OD requests');
  return Array.isArray(json.data) ? json.data : [];
}

export async function createOdRequest(payload) {
  const res = await fetch(`${API_BASE}/academics/attendance/od-requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await parseResponse(res, 'Failed to create OD request');
  return json.data;
}

export async function updateOdRequest(requestId, payload) {
  const res = await fetch(`${API_BASE}/academics/attendance/od-requests/${encodeURIComponent(requestId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await parseResponse(res, 'Failed to update OD request');
  return json.data;
}

export async function reviewOdRequestStatus(requestId, payload) {
  const res = await fetch(`${API_BASE}/academics/attendance/od-requests/${encodeURIComponent(requestId)}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await parseResponse(res, 'Failed to update OD status');
  return json.data;
}

export async function deleteOdRequestById(requestId) {
  const res = await fetch(`${API_BASE}/academics/attendance/od-requests/${encodeURIComponent(requestId)}`, {
    method: 'DELETE',
  });
  await parseResponse(res, 'Failed to delete OD request');
}
