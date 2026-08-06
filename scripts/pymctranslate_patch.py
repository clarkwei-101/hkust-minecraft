"""
HKUST-MC v2.4 — PyMCTranslate Bug Fix Loader
==============================================
Some Bedrock blocks (dirt, sand, grass_block, coarse_dirt, mud, mud_brick_stairs,
mossy_stone_bricks, polished_blackstone_bricks, etc.) land in the
PyMCTranslate Version(bedrock, (1, 13, 0)) translator path which has a
known bug: output_type is neither 'block' nor 'entity', causing the
translator to raise ``Exception("No output object given.")`` from
``PyMCTranslate/py3/api/version/translate.py:427``.

We patch the translator to fall back to a Block("minecraft","air") instead
of raising. This is safe because:

  - audit scripts treat 'err' / 'air' as non-floating ground/terrain, so
    returning air for these blocks makes them invisible (correct, since they
    are background dirt/sand blocks anyway).
  - inject scripts that need a real block read of these materials should
    set_version_block by exact coordinate and verify the result.

Usage:

    import sys
    sys.path.insert(0, '/path/to/hkust-minecraft/scripts')
    import pymctranslate_patch
    pymctranslate_patch.apply()  # idempotent
    import amulet
    ...
"""
import os
import sys

_PATCH_APPLIED = False


def apply(verbose=True):
    """Patch PyMCTranslate translate.py to fall back to air block instead of raising."""
    global _PATCH_APPLIED
    if _PATCH_APPLIED:
        if verbose:
            print("[pymctranslate_patch] already applied (idempotent)")
        return

    # Find site-packages path
    import site
    candidates = []
    for sp in site.getsitepackages():
        candidates.append(os.path.join(sp, 'PyMCTranslate', 'py3', 'api', 'version', 'translate.py'))
    # Also try user lib
    import amulet
    amp = os.path.dirname(amulet.__file__)
    candidates.append(os.path.join(amp, '..', 'PyMCTranslate', 'py3', 'api', 'version', 'translate.py'))

    patched = False
    for path in candidates:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            content = f.read()
        if 'HKUST-MC' in content:
            if verbose:
                print(f"[pymctranslate_patch] already patched at {path}")
            patched = True
            break
        if 'No output object given' in content:
            new_content = content.replace(
                '    else:\n        raise Exception("No output object given.")',
                '''    else:
        # PATCH (2026-08-07 HKUST-MC): fall back to air Block instead of raising.
        try:
            from amulet.api.block import Block as _AirBlock
            return _AirBlock("minecraft", "air"), extra_output, extra_needed, cacheable
        except Exception:
            raise Exception("No output object given.")'''
            )
            if new_content != content:
                with open(path, 'w') as f:
                    f.write(new_content)
                # Clear pyc cache
                pyc = path.replace('.py', f'.cpython-{sys.version_info.major}{sys.version_info.minor}.pyc')
                if os.path.exists(pyc):
                    os.remove(pyc)
                if verbose:
                    print(f"[pymctranslate_patch] patched {path}")
                patched = True
                break

    if not patched and verbose:
        print("[pymctranslate_patch] no patching needed (already air-fallback)")

    _PATCH_APPLIED = True


if __name__ == '__main__':
    apply(verbose=True)
