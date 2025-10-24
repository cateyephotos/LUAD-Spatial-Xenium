# Planning Documentation - LUAD-Spatial-Xenium Project

## Overview

This folder contains comprehensive planning and reference documentation for transforming the LUAD-Spatial project to support **Xenium OME-TIFF integration** with PhenoCycler QPTIFF files, while maintaining backward compatibility with the existing Visium pipeline.

**Created**: 2025-10-23
**Status**: PLANNING PHASE

---

## Document Guide

### 1. **PROJECT_OVERVIEW.md** ⭐ START HERE
- Current project status and implementation
- Project goals for Xenium integration
- Key differences between Visium and Xenium
- Proposed architecture changes
- High-level roadmap

### 2. **QUICK_REFERENCE.md** 📋 QUICK LOOKUP
- One-page summary of goals
- Key files to delete/refactor/keep
- Hardcoded elements to extract
- Processing pipeline overview
- Success metrics

### 3. **CURRENT_IMPLEMENTATION_ANALYSIS.md** 🔍 DEEP DIVE
- Detailed file structure
- Current processing pipeline details
- Hardcoded elements and parameters
- Dependencies and data formats
- Output structure

### 4. **TECHNICAL_SPECIFICATIONS.md** 🛠️ DESIGN DETAILS
- Data format specifications (Xenium, PhenoCycler, OME-TIFF)
- Mask generation algorithms
- Alignment algorithm details
- Resolution handling strategy
- Configuration system design
- API design and usage examples
- Performance targets

### 5. **REFACTORING_ROADMAP.md** 🗺️ IMPLEMENTATION PLAN
- 4-phase implementation strategy
- Detailed tasks for each phase
- Abstraction layer design
- Modularization plan
- Pipeline refactoring approach
- Backward compatibility strategy
- Testing strategy

### 6. **CODE_CLEANUP_GUIDE.md** 🧹 DELETION & MODIFICATION
- Files to DELETE (9 files)
- Files to REFACTOR (3 files)
- Files to KEEP (4 files)
- Hardcoded values to extract
- Directory structure changes
- Deletion priority and phases
- Backward compatibility maintenance

### 7. **IMPLEMENTATION_LOG.md** 📝 PROGRESS TRACKING
- Detailed task checklist for all 4 phases
- Status tracking for each task
- Code deletion checklist
- Notes and issues
- Progress summary table
- **Update this as work progresses**

---

## Key Findings

### Current State
- **8-step pipeline** specifically designed for LUAD3B sample
- **Hardcoded parameters** throughout codebase
- **Sample-specific logic** (if/elif blocks for different samples)
- **Tightly coupled** to Visium and PhenoCycler formats
- **~2,500 lines** of core processing code

### Main Issues
1. **Sample-specific hardcoding** (FFPE_LUAD_2_C, FFPE_LUAD_3_B, FFPE_LUAD_4_C)
2. **Hardcoded thresholds** (binary_th, hole_th, tiss_th)
3. **Fixed page selection** for PhenoCycler ([22, 4, 0, 1, 2, 10, 12, 21])
4. **Fiducial detection** only for Visium
5. **No configuration system**
6. **No abstraction layer** for different data formats

### Refactoring Scope
- **DELETE**: 9 DOIT_* orchestrator scripts
- **REFACTOR**: 3 main processing scripts (Parse_Visium_HE.py, Parse_PhenoCycler_QP.py, Align_Visium-PhenoCycler.py)
- **KEEP**: 4 utility modules
- **CREATE**: ~10 new modular components

---

## Implementation Timeline

| Phase | Duration | Focus | Status |
|-------|----------|-------|--------|
| 1 | 2 weeks | Abstraction layer, config system | NOT STARTED |
| 2 | 2 weeks | Modularize processors, alignment | NOT STARTED |
| 3 | 2 weeks | Unified pipeline, remove DOIT_* | NOT STARTED |
| 4 | 2 weeks | Xenium support, testing | NOT STARTED |
| **Total** | **8 weeks** | **Full refactoring** | **PLANNING** |

---

## Success Criteria

✅ Support Xenium OME-TIFF files
✅ Support arbitrary OME-TIFF files
✅ Maintain Visium-PhenoCycler compatibility
✅ Remove all sample-specific hardcoding
✅ Configurable parameters (YAML)
✅ Modular, reusable components
✅ Comprehensive documentation
✅ Unit and integration tests
✅ Performance: < 30 min full pipeline

---

## How to Use This Documentation

### For Project Managers
1. Read **PROJECT_OVERVIEW.md** for goals
2. Review **REFACTORING_ROADMAP.md** for timeline
3. Track progress in **IMPLEMENTATION_LOG.md**

### For Developers
1. Start with **QUICK_REFERENCE.md** for overview
2. Read **CURRENT_IMPLEMENTATION_ANALYSIS.md** for details
3. Follow **REFACTORING_ROADMAP.md** for implementation
4. Use **CODE_CLEANUP_GUIDE.md** for specific changes
5. Update **IMPLEMENTATION_LOG.md** as you work

### For Code Review
1. Check **TECHNICAL_SPECIFICATIONS.md** for design
2. Verify against **CODE_CLEANUP_GUIDE.md**
3. Validate with **IMPLEMENTATION_LOG.md**

---

## Next Steps

1. **Review** all documentation
2. **Approve** refactoring roadmap
3. **Assign** tasks from IMPLEMENTATION_LOG.md
4. **Begin** Phase 1 (abstraction layer)
5. **Update** IMPLEMENTATION_LOG.md weekly
6. **Schedule** phase reviews

---

## Document Maintenance

- **Update IMPLEMENTATION_LOG.md** after each task
- **Add notes** for blockers and decisions
- **Review** quarterly for accuracy
- **Archive** completed phases

---

## Questions?

Refer to the specific document sections or create an issue in the repository.

**Last Updated**: 2025-10-23
**Next Review**: (To be scheduled)

