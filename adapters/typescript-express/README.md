# CMB Boundary Adapter - TypeScript + Express

This adapter implements the same `cmb.boundary-event.v1` semantics as the Python reference engine and runs the shared cases in `../../conformance/boundary.v1.cases.json`.

## Install and test

```bash
npm install
npm run build
npm test
```

The package intentionally pins the current Express 5.2.1 and TypeScript 7.0.2 top-level versions used for this reference adapter. Dependency lockfiles should be committed before publishing or deploying this example as an independent package.

## Run

```bash
npm run build
npm start
```

POST a complete boundary event to:

```text
/cmb/boundary/v1
```

Responses:

- `200` - boundary allowed;
- `422` - valid event rejected by CMB policy;
- `400` - malformed or unsupported boundary event.

## Security boundary

Do not accept client-supplied booleans as authoritative evidence of consent, disclosure, or human-review availability in a production system. Derive those facts from authenticated application state and verified workflow records.

This adapter does not classify people and does not infer identity, diagnosis, intent, mental state, or moral status from text.
