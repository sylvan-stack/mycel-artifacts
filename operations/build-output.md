---
role: authored
---
# Build and test output locations

<!-- mycel:cues
type: literal
match: ["build artifacts", "build output directory", "build the app", "build this app", "build the tool", "build this tool", "package the app", "package this app", "package the tool", "package this tool", "stage a build", "arbol-builds build", "mycel_build create", "mycel_build prepare", "package_build.py --candidate", "uv build", "npm run build", "xcodebuild", "swift build", "cargo build", "go build", "cmake --build"]
-->

For Sylvan Stack, follow [Building Sylvan Stack components](../../forester/operations/sylvan-stack-builds.md).
Forester tracks identifiable temporary output. At or below 10 GB of
allocated space in `~/Builds`, it waits for two hours without build
activity. Above 10 GB, eligible builds get at least five minutes after
the build command exits before Forester removes them oldest first. Use
`forester builds keep <path> --minutes 30` when qualification needs longer.
The maximum is 60 minutes from build completion. Keep one stable installation
per app. Put only its runnable entry points and complete native app bundles
under `~/Applications/<app>/`, and route its global hotkeys there. Keep
source, standalone dependencies and build data in managed locations
outside Applications. Keep Temporary Builds under `~/Builds/`, including
qualified candidates awaiting promotion.

- **Build registries** live under `~/Builds`. The installed registries are
  `~/Builds/registries/arbol/` and `~/Builds/registries/mycel/`. Forester
  includes retired diagnostics in the same size and inactivity policy.
  It retires unused runtime payloads after the inactivity period.
  Stable entry points start the installed copy from Applications without
  reading the registries.
- **Retained outputs and test runtimes** use a new private directory at
  `~/Builds/<org>/<repo>/<run-id>/` or `~/Builds/<repo>/<run-id>/` for a
  standalone repository. The directory holds binaries, bundles, staged
  dependencies, test homes and other files needed to inspect or rerun that run.
  The build or test command gets this destination before it starts.
  `~/Builds` holds disposable output (Owner Goals OG-2 and OG-3). Keep
  the source revision so the run can be rebuilt after Forester removes it.
- **Backups and older material worth keeping** go to the external drive
  Mercury, never to `~/Builds` (OG-4). Arbol's go to
  `/Volumes/Mercury/Arbol/backups/`.
- **Disposable runs** use a fresh directory under `~/Builds/`. Cleanup
  follows completion and recording the results.
- **Reports and documentation** go in the repository's `artifact_root` under
  `~/Artifacts`. Reports that depend on retained output record its path and
  source revision; the source revision is what reproduces it once the output
  is gone.

### Release completed Arbol runs

To release a legacy run, the build or test runner calls the Arbol release
command as its final step,
after its processes have exited, its disk images have been detached, and its
evidence is saved outside `~/Builds`. Invoke
`arbol-builds release-run <run-directory> --evidence <saved-report>` only for
output the runner has finished using. Keep runs that still supply inputs for
follow-up work. See [BLD-1](../../arbol/builds/01-run-output-cleanup.md).
