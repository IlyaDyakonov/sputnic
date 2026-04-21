"use client";

import { FormEvent, useEffect, useState } from "react";
import { Alert, Col, Container, Row } from "react-bootstrap";

import { AlertsTable } from "../components/alerts-table";
import { FilesTable } from "../components/files-table";
import { PageHeader } from "../components/page-header";
import { UploadFileModal } from "../components/upload-file-modal";
import { downloadFileUrl, fetchAlerts, fetchFiles, uploadFile } from "../lib/api";
import { AlertItem } from "../types/alert";
import { FileItem } from "../types/file";

export default function Page() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([fetchFiles(), fetchAlerts()]);

      setFiles(filesData);
      setAlerts(alertsData);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      setErrorMessage("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await uploadFile({ title: title.trim(), file: selectedFile });
      setShowModal(false);
      setTitle("");
      setSelectedFile(null);
      await loadData();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <PageHeader onRefresh={() => void loadData()} onCreate={() => setShowModal(true)} />

          {errorMessage ? (
            <Alert variant="danger" className="shadow-sm">
              {errorMessage}
            </Alert>
          ) : null}

          <FilesTable files={files} isLoading={isLoading} getDownloadUrl={downloadFileUrl} />
          <AlertsTable alerts={alerts} isLoading={isLoading} />
        </Col>
      </Row>

      <UploadFileModal
        show={showModal}
        title={title}
        isSubmitting={isSubmitting}
        onTitleChange={setTitle}
        onFileChange={setSelectedFile}
        onClose={() => setShowModal(false)}
        onSubmit={handleSubmit}
      />
    </Container>
  );
}
