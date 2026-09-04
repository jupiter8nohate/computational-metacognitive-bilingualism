import express from "express";
import { fileURLToPath } from "node:url";

import { evaluateBoundary } from "./boundary.js";

export const app = express();

app.disable("x-powered-by");
app.use(express.json({ limit: "16kb", strict: true }));

app.post("/cmb/boundary/v1", (request, response) => {
  try {
    const decision = evaluateBoundary(request.body);
    response.status(decision.allowed ? 200 : 422).json(decision);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "invalid boundary event";
    response.status(400).json({
      error: "INVALID_BOUNDARY_EVENT",
      message,
    });
  }
});

const isDirectExecution =
  process.argv[1] !== undefined &&
  fileURLToPath(import.meta.url) === process.argv[1];

if (isDirectExecution) {
  const port = Number.parseInt(process.env.PORT ?? "8000", 10);
  app.listen(port, "127.0.0.1", () => {
    process.stdout.write(`CMB boundary adapter listening on http://127.0.0.1:${port}\n`);
  });
}
