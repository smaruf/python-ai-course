import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  StyleSheet,
  Platform,
  SafeAreaView,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";

const API_URL = "http://localhost:8000";

export default function HomeScreen() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const pickAndProcess = async () => {
    const picked = await DocumentPicker.getDocumentAsync({
      type: ["application/pdf", "text/plain"],
    });
    if (picked.canceled) return;

    const asset = picked.assets[0];
    setLoading(true);
    setResult("");
    setStatus("Uploading…");

    const form = new FormData();
    form.append("file", {
      uri: asset.uri,
      name: asset.name,
      type: asset.mimeType ?? "application/octet-stream",
    } as unknown as Blob);
    form.append("prompt", prompt);

    try {
      const response = await fetch(`${API_URL}/api/documents/process-stream`, {
        method: "POST",
        body: form,
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const payload = JSON.parse(line.slice(6));
            if (payload.token) setResult((prev) => prev + payload.token);
            if (payload.status) setStatus(payload.status);
          }
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>📄 AI Document Processor</Text>
        <Text style={styles.subtitle}>Mobile · {Platform.OS}</Text>

        <TextInput
          style={styles.input}
          placeholder="Custom prompt (optional)"
          value={prompt}
          onChangeText={setPrompt}
        />

        <TouchableOpacity style={styles.button} onPress={pickAndProcess} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Pick Document ▶</Text>
          )}
        </TouchableOpacity>

        {status ? <Text style={styles.status}>{status}</Text> : null}
        {result ? <Text style={styles.result}>{result}</Text> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#fff" },
  container: { padding: 20 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 4 },
  subtitle: { fontSize: 13, color: "#888", marginBottom: 16 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    padding: 10,
    marginBottom: 12,
  },
  button: {
    backgroundColor: "#2563eb",
    borderRadius: 6,
    padding: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  buttonText: { color: "#fff", fontWeight: "600" },
  status: { color: "#555", marginBottom: 8 },
  result: {
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    fontSize: 13,
    backgroundColor: "#f4f4f4",
    padding: 12,
    borderRadius: 4,
  },
});
