import { API_BASE_URL } from "./config";
import { AlertItem } from "../types/alert";
import { FileItem } from "../types/file";

export async function fetchFiles(): Promise<FileItem[]> {
  const response = await fetch(`${API_BASE_URL}/files`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Не удалось загрузить файлы");
  }
  return response.json() as Promise<FileItem[]>;
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const response = await fetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Не удалось загрузить алерты");
  }
  return response.json() as Promise<AlertItem[]>;
}

export async function uploadFile(payload: { title: string; file: File }): Promise<void> {
  const formData = new FormData();
  formData.append("title", payload.title);
  formData.append("file", payload.file);

  const response = await fetch(`${API_BASE_URL}/files`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Не удалось загрузить файл");
  }
}

export function downloadFileUrl(fileId: string): string {
  return `${API_BASE_URL}/files/${fileId}/download`;
}
