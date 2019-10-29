# General setup

Hierarchy
- core
- core.contrib
- custom

Tools can decide what to support.
Example Ilastik: We only support core and maybe contrib.

Dependencies need to be compatible with core / contrib dependencies.
E.g. needs to run with the same pytorch and numpy version.
Additional dependencies can be added for custom stuff.

How does this core library actually work?
Generic core library -> Implementations
Reference Implementation -> Generate generic representation

Can we decide on function signatures for the different steps:
- preprocessing
- loss
- etc.
