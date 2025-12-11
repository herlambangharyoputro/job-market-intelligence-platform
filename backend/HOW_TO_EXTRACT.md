# 📦 Cara Download & Extract Files

## ✅ File yang Tersedia

Ada 2 cara untuk download files:

### Option 1: Download Archive (RECOMMENDED)
**File:** `annotation-system-complete.tar.gz` (29 KB)

**Berisi:**
- Semua 15 migration files
- Scripts (run_migrations.py, seed_initial_data.py)
- Documentations (4 files)
- Configuration files (alembic.ini, env.py, etc)

### Option 2: Download Individual Files
Jika archive tidak bisa di-download, download file-file individual:

**Must Have:**
1. `00_README_START_HERE.md` - Panduan utama
2. `01_DELIVERY_SUMMARY.md` - Checklist lengkap
3. `run_migrations.py` - Script run migrations
4. `seed_initial_data.py` - Script seed data
5. `alembic.ini` - Konfigurasi Alembic

**Migration Files (15 files):**
- Semua file di folder `alembic/versions/`
- Format: `XXX_create_[table_name].py`

---

## 🔧 Cara Extract Archive

### Windows (PowerShell)
```powershell
# Extract menggunakan tar (Windows 10+)
tar -xzf annotation-system-complete.tar.gz

# Atau gunakan 7-Zip / WinRAR
# Right click → Extract Here
```

### Linux/Mac
```bash
# Extract
tar -xzf annotation-system-complete.tar.gz

# View contents tanpa extract
tar -tzf annotation-system-complete.tar.gz
```

---

## 📁 Struktur Setelah Extract

```
annotation-system-complete/
├── README.md                          # Baca ini dulu!
├── DELIVERY_SUMMARY.md
├── DOCUMENTATION.md
├── alembic.ini
├── run_migrations.py
├── seed_initial_data.py
└── alembic/
    ├── README.md
    ├── env.py
    ├── script.py.mako
    └── versions/
        ├── 001_create_jobs_table.py
        ├── 002_create_annotation_types.py
        ├── ... (13 more files)
        └── 015_create_benefit_categories.py
```

---

## 🚀 Setup di Project Anda

### Step 1: Extract Archive
```bash
# Extract di Downloads folder
cd ~/Downloads
tar -xzf annotation-system-complete.tar.gz
```

### Step 2: Copy ke Project
```bash
# Copy semua files ke backend project
cp -r annotation-system-complete/* D:/job-market-intelligence-platform/backend/

# Atau di Windows (PowerShell):
Copy-Item -Path "annotation-system-complete\*" -Destination "D:\job-market-intelligence-platform\backend\" -Recurse
```

### Step 3: Verify Files
```bash
cd D:/job-market-intelligence-platform/backend

# Check alembic folder
dir alembic

# Check migration files
dir alembic\versions

# Should have 15 files: 001 to 015
```

### Step 4: Run Migrations
```bash
# Pastikan di backend directory
cd D:/job-market-intelligence-platform/backend

# Run migrations
python run_migrations.py

# Or menggunakan Alembic langsung
alembic upgrade head
```

### Step 5: Seed Initial Data
```bash
python seed_initial_data.py
```

---

## ⚠️ Troubleshooting

### Issue: "tar command not found" (Windows)
**Solution:**
1. Gunakan 7-Zip atau WinRAR
2. Update ke Windows 10 version 1803+ (tar included)
3. Install Git for Windows (includes tar)

### Issue: Archive corrupted
**Solution:**
1. Re-download file
2. Check file size: should be ~29 KB
3. Try download dengan browser lain

### Issue: Permission denied saat copy
**Solution:**
```bash
# Windows: Run PowerShell as Administrator
# Linux/Mac: Use sudo
sudo cp -r annotation-system-complete/* /path/to/project/
```

---

## 📞 Alternative Methods

### Method 1: Manual Download dari UI
1. Click file `annotation-system-complete.tar.gz`
2. Click Download button
3. Save ke Downloads folder
4. Extract menggunakan 7-Zip/WinRAR
5. Copy ke project folder

### Method 2: Download Individual Files
Jika archive tidak work:
1. Download `00_README_START_HERE.md`
2. Download `run_migrations.py`
3. Download `seed_initial_data.py`
4. Download `alembic.ini`
5. Create folder `alembic/versions/`
6. Download semua 15 migration files one by one
7. Download `alembic/env.py`
8. Download `alembic/script.py.mako`

### Method 3: Recreate Manual
Jika semua gagal, bisa recreate manual dari documentation:
1. Buka `01_DELIVERY_SUMMARY.md`
2. Follow struktur yang dijelaskan
3. Copy paste code dari setiap section

---

## ✅ Verification Checklist

Setelah extract & copy, verify:

- [ ] Folder `alembic/` ada di backend project
- [ ] Folder `alembic/versions/` berisi 15 files
- [ ] File `alembic.ini` ada di backend root
- [ ] File `run_migrations.py` ada di backend root
- [ ] File `seed_initial_data.py` ada di backend root
- [ ] File `alembic/env.py` ada
- [ ] File `alembic/script.py.mako` ada

**Total Files:** 23 files minimum

---

## 🎯 Next Steps After Setup

1. ✅ Extract archive
2. ✅ Copy to project
3. ✅ Verify files
4. ⏳ Run migrations (Phase 1)
5. ⏳ Seed initial data
6. ⏳ Verify tables created
7. ⏳ Start Phase 2 (XLSX migration)

---

## 📚 Need Help?

1. **Read README.md first** - Comprehensive guide
2. **Check DELIVERY_SUMMARY.md** - Detailed checklist
3. **Review alembic/README.md** - Migration specific help
4. **Check DOCUMENTATION.md** - Technical reference

---

**Files Ready!** ✅
**Total Size:** ~29 KB compressed, ~150 KB uncompressed
**Files Count:** 23 files (15 migrations + 8 support files)
