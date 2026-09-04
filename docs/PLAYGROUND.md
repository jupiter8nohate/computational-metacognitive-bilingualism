# Interactive CMB Playground

The repository now includes a zero-dependency browser playground at:

**[Open the local/static playground](playground/index.html)**

It is designed to make CMB understandable before a visitor reads the full specifications.

## What it does

- accepts a human statement;
- computes a local SHA-256 digest in the browser;
- projects the statement through the 13 CMB-Z13 symbolic lenses;
- creates a machine-readable declaration without claiming the declaration is the person;
- evaluates explicit boundary-policy facts using the same five rules as the Python reference engine.

## What it does not do

The playground is **not a compiler or transpiler**. It does not convert arbitrary source code into 13 equivalent executable programs.

The Z13 output is a symbolic lens projection intended for education, code-poetry, and structured reasoning.

The SHA-256 digest is an integrity primitive, not a signature, timestamp, authorship proof, copyright registration, or legal judgment.

The browser tool runs locally and has no analytics or external JavaScript dependencies.

## Deployment

MkDocs copies the standalone page into the generated documentation site. Once GitHub Pages is enabled for this repository, the same artifact can function as the public CMB interactive front door.

For the executable Python policy engine, see [For developers](DEVELOPERS.md).
