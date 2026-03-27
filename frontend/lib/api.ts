const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAgents() {
  const response = await fetch(`${API_URL}/api/agents`);
  if (!response.ok) throw new Error("Failed to fetch agents");
  return response.json();
}

export async function createTask(workflowId: string, inputData: any) {
  const response = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workflow_id: workflowId,
      input_data: inputData,
    }),
  });
  if (!response.ok) throw new Error("Failed to create task");
  return response.json();
}

export async function getTaskResult(taskId: string) {
  const response = await fetch(`${API_URL}/api/tasks/${taskId}`);
  if (!response.ok) throw new Error("Failed to fetch task");
  return response.json();
}