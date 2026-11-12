# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |
| < 0.1 | ❌ |

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Use GitHub's private vulnerability reporting:

1. Open the repository on GitHub.
2. Go to **Security** → **Advisories** → **Report a vulnerability**.
3. Include a minimal reproduction, affected version, and impact.

If private reporting is unavailable, contact a maintainer through the contact
method listed on their GitHub profile.

We aim to acknowledge reports within 7 days and to publish a coordinated fix
when the issue is confirmed.

## Scope

This project processes local images and writes local SVG/PNG/JSON files. It
does not run a server and does not upload user images anywhere.

Relevant security areas include:

- malformed images that crash the parser;
- path traversal through `--out` or file names;
- denial of service from extremely large images;
- SVG output containing unescaped text from a hint file.

## Safe usage

- Do not run the tool on untrusted images with elevated privileges.
- Review generated SVG before embedding it in a public website if the hint
  labels come from an untrusted source.
- Keep dependencies updated.
