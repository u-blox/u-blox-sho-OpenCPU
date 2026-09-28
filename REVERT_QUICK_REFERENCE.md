# Quick Revert Commands for Master Branch

**TL;DR - Copy/paste this if you're an admin:**

## For Admin with GitLab Access (Cleanest)

```bash
cd e:/u-blox/u-blox-sho-OpenCPU
git fetch origin
git reset --hard 96a01a3
git push -f origin master:master
```

**Verify it worked:**
```bash
git log --oneline -1 origin/master
# Should show: 96a01a3
```

## For Admin Without Forcing History (Better for Audit Trail)

```bash
cd e:/u-blox/u-blox-sho-OpenCPU
git fetch origin
git reset --hard 96a01a3
git revert -n 0c1348b
git revert -n 1a4b97c
git revert -n 2434e3f
git commit -m "Revert consolidation commits - preserving cmag_getting_started_sdk branch for review"
git push origin master
```

**Verify:**
```bash
git log --oneline -3 origin/master
# Should show revert commits
```

## What Gets Reverted

These consolidation commits will be undone:
- `2434e3f` - Restructure to unified GettingStartedSDK folder
- `1a4b97c` - Move BUILD_ALL_EXAMPLES.md and QUICK_BUILD_REFERENCE.md  
- `0c1348b` - Clean up old Getting Started folders

## What Stays Safe

✅ `cmag_getting_started_sdk` branch - All consolidation work preserved  
✅ `feature/restructure-getting-started` - Original feature branch  
✅ All other branches - Untouched

## Why It's Strange We Could Push

Good catch! Either:
1. Master protection was set up AFTER we pushed
2. Someone with admin access pushed it
3. The initial merge didn't trigger protection checks

**After revert:** Test that protection works by trying normal push (should fail)

---

**Read full instructions in:** `MASTER_REVERT_INSTRUCTIONS.md`
