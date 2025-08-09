# MP4 to 1920x1080 Converter with GPU Acceleration

A fast Python script that batch converts all MP4 files to 1920x1080 resolution with GPU acceleration, maintaining aspect ratio using black bars when needed.

## 🚀 Features

- **GPU Accelerated**: Auto-detects and uses NVIDIA NVENC, AMD AMF, or Intel QuickSync
- **Batch Processing**: Converts all MP4 files in a directory
- **Aspect Ratio Preservation**: Adds black bars to maintain original aspect ratio
- **Real-time Progress**: Shows percentage completion and encoding FPS
- **Smart Skipping**: Skips files already at 1920x1080 resolution
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Fastest Presets**: Uses the fastest encoding presets for maximum speed

## 📋 Requirements

### Software Requirements
- **Python 3.6+**
- **FFmpeg** (with ffprobe)
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

### GPU Requirements (Optional but Recommended)

#### NVIDIA GPUs
- **GPU**: GTX 10-series or newer (RTX series recommended)
- **Drivers**: Latest GeForce drivers with NVENC support
- **Encoder**: Uses `h264_nvenc` with fastest presets

#### AMD GPUs
- **GPU**: RX 400-series or newer
- **Drivers**: Latest Radeon drivers with AMF support
- **Encoder**: Uses `h264_amf` for hardware acceleration

#### Intel GPUs
- **GPU**: Intel HD Graphics 4000 or newer with QuickSync
- **Drivers**: Latest Intel graphics drivers
- **Encoder**: Uses `h264_qsv` for hardware acceleration

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/henkdetenk12345/mp4-1080p-converter.git
   cd mp4-1080p-converter
   ```

2. **Install FFmpeg** (if not already installed)

3. **Run the script:**
   ```bash
   python mp4_converter.py
   ```

## 💻 Usage

### Basic Usage
Place the script in the directory containing your MP4 files and run:
```bash
python mp4_converter.py
```

### Custom Directories
Edit the script configuration:
```python
INPUT_DIR = "/path/to/your/videos"    # Source directory
OUTPUT_DIR = "/path/to/output"        # Output directory (None = auto-create 'converted' folder)
```

### Expected Output
```
🎬 MP4 to 1920x1080 Converter with GPU Acceleration
==================================================
✅ Using encoder: NVIDIA NVENC (h264_nvenc)
Found 75 MP4 file(s)
Output directory: .\converted
--------------------------------------------------

[1/75] Processing: video1.mp4
📹 Original resolution: 1440x1080
⏱️  Duration: 1526.1 seconds
🔄 Starting conversion...
🔄 Progress: 45.2% - 687.3 fps
```

## ⚙️ How It Works

### GPU Encoder Detection
The script automatically detects the best available encoder:
1. **NVIDIA NVENC** (`h264_nvenc`) - Fastest for NVIDIA GPUs
2. **AMD AMF** (`h264_amf`) - Optimized for AMD GPUs  
3. **Intel QuickSync** (`h264_qsv`) - For Intel integrated graphics
4. **CPU Fallback** (`libx264`) - If no GPU encoder available

### Aspect Ratio Handling
- **4:3 videos** → Adds black bars on sides to fit 16:9
- **Ultra-wide videos** → Adds black bars top/bottom
- **16:9 videos** → Direct scaling to 1920x1080
- **Already 1920x1080** → Skipped automatically

### Encoding Settings
- **Quality**: CRF 23 equivalent (high quality)
- **Speed**: Fastest presets for each encoder
- **Audio**: Copy without re-encoding (faster)
- **Output**: Progressive scan, web-optimized

## 📊 Performance

### Real-world Test Results
**Test System**: Windows 11, Ryzen 7 5800X, RTX 3060
- **Single video**: ~22 minutes → ~1.5 minutes encoding time
- **Encoding speed**: 500-700 fps (with thermal variations 400-700 fps)
- **Speedup**: ~15x faster than real-time
- **Batch of 75 videos**: ~2-3 hours total

### Speed Comparison
- **CPU only** (libx264): ~400 fps
- **NVENC** (RTX 3060): 500-700 fps (2-3x faster than CPU)
- **Real-time ratio**: 15-30x faster than video duration

### GPU Utilization
- **Power usage**: 30-40% of GPU capacity  
- **Temperature**: 40-50°C (thermal cycling affects FPS)
- **Memory**: Minimal VRAM usage (~1-2GB)
- **System impact**: Can run other tasks simultaneously

## 🔧 Optimization Tips

### For NVIDIA Users
1. **NVIDIA Control Panel** → Manage 3D Settings:
   - Power Management Mode: "Prefer maximum performance"
   - Low Latency Mode: "On"

2. **MSI Afterburner/GPU Tweak** (optional):
   - Increase power limit to maximum
   - Ensure adequate cooling

### For AMD Users
- Use latest Radeon drivers
- Enable Radeon Chill if temperatures get high

### For Intel Users
- Update to latest Intel graphics drivers
- Enable hardware acceleration in Intel Graphics Command Center

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found"**
- Install FFmpeg and ensure it's in your system PATH
- Test with: `ffmpeg -version`

**"No GPU encoder found"**
- Update GPU drivers
- Verify hardware encoding support for your GPU model

**Low FPS performance**
- Check GPU temperature and thermal throttling
- Verify power management settings
- Close other GPU-intensive applications

**Script hangs at start**
- Some antivirus software blocks FFmpeg - add exception
- Check if input files are corrupted or inaccessible

### Performance Issues
If encoding FPS drops significantly:
1. Check GPU temperature (should be <80°C)
2. Verify GPU isn't downclocking in GPU monitoring software
3. Set Windows power plan to "High Performance"
4. Close unnecessary background applications

## 📝 Configuration Options

Edit these variables at the bottom of the script:
```python
INPUT_DIR = "."                    # Source directory
OUTPUT_DIR = None                  # Output directory (None = auto-create)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FFmpeg](https://ffmpeg.org/) - the leading multimedia framework
- GPU acceleration powered by NVENC, AMF, and QuickSync technologies
- Inspired by the need for fast, reliable batch video processing

## 💡 Tips for Best Results

- **Use SSD storage** for input/output to maximize speed
- **Close heavy applications** during batch processing for optimal GPU performance  
- **Monitor temperatures** during long batch jobs
- **Sort by file size** - process larger files when system is coolest
- **Use dedicated output drive** to avoid I/O bottlenecks
