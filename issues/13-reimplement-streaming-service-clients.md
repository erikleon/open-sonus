# Issue 13: Reimplement streaming service clients

- Status: Rejected
- Source: `TODOS.md`
- Why rejected: Keeps the repository distributable, sponsorable, and app-store safe; users can install grey-area providers themselves.

## Summary

Do not reimplement streaming service clients in the project repository.

## Acceptance criteria

- [ ] Maintain an out-of-tree provider plugin boundary.
- [ ] Keep direct support to the planned providers: local media, Jellyfin, Navidrome, Subsonic, and radio.
- [ ] Avoid in-repo implementations that create legal or distributability risk.
