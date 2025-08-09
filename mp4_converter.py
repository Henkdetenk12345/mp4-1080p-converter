import os
import subprocess
import glob
import re
from pathlib import Path

def get_video_info(video_path):
    """Get video information using ffprobe"""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse output for width and height
        width_match = re.search(r'"width":\s*(\d+)', result.stdout)
        height_match = re.search(r'"height":\s*(\d+)', result.stdout)
        duration_match = re.search(r'"duration":\s*"([^"]+)"', result.stdout)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            duration = float(duration_match.group(1)) if duration_match else 0
            return width, height, duration
        return None, None, 0
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None, None, 0

def detect_gpu_encoder():
    """Detect available GPU encoder"""
    encoders = [
        ('h264_nvenc', 'NVIDIA NVENC'),
        ('h264_amf', 'AMD AMF'),
        ('h264_qsv', 'Intel QuickSync'),
        ('libx264', 'CPU (fallback)')
    ]
    
    for encoder, name in encoders:
        try:
            cmd = ['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                   '-c:v', encoder, '-f', 'null', '-']
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Using encoder: {name} ({encoder})")
                return encoder
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("⚠️  No GPU encoder found, using CPU")
    return 'libx264'

def convert_video(input_path, output_path, original_width, original_height, gpu_encoder):
    """Convert video to 1920x1080 with black bars if needed"""
    
    # Determine if we need padding
    aspect_ratio = original_width / original_height
    target_aspect = 1920 / 1080
    
    if aspect_ratio > target_aspect:
        # Video is wider - add black bars top and bottom
        scale_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:black"
    else:
        # Video is taller or correct ratio - add black bars left and right
        scale_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:black"
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', scale_filter,
        '-c:v', gpu_encoder,
        '-c:a', 'copy',  # Don't re-encode audio
        '-y',  # Overwrite output file
        '-stats',  # Show statistics during encoding
        output_path
    ]
    
    # GPU-specific settings
    if 'nvenc' in gpu_encoder:
        # NVIDIA NVENC settings
        cmd.insert(-3, '-preset')
        cmd.insert(-3, 'p1')  # Fastest preset for NVENC
        cmd.insert(-3, '-tune')
        cmd.insert(-3, 'hq')  # High quality tune
        cmd.insert(-3, '-rc')
        cmd.insert(-3, 'vbr')  # Variable bitrate
        cmd.insert(-3, '-cq')
        cmd.insert(-3, '23')  # Quality setting (similar to CRF)
    elif 'amf' in gpu_encoder:
        # AMD AMF settings
        cmd.insert(-3, '-usage')
        cmd.insert(-3, 'transcoding')
        cmd.insert(-3, '-rc')
        cmd.insert(-3, 'cqp')
        cmd.insert(-3, '-qp_i')
        cmd.insert(-3, '23')
        cmd.insert(-3, '-qp_p')
        cmd.insert(-3, '23')
    elif 'qsv' in gpu_encoder:
        # Intel QuickSync settings
        cmd.insert(-3, '-preset')
        cmd.insert(-3, 'veryfast')
        cmd.insert(-3, '-global_quality')
        cmd.insert(-3, '23')
    else:
        # CPU fallback
        cmd.insert(-3, '-preset')
        cmd.insert(-3, 'ultrafast')
        cmd.insert(-3, '-crf')
        cmd.insert(-3, '23')
    
    return cmd

def parse_progress(line, duration):
    """Parse ffmpeg progress output"""
    if 'out_time_us=' in line:
        try:
            time_us = int(line.split('=')[1].strip())
            time_seconds = time_us / 1000000
            if duration > 0:
                percentage = (time_seconds / duration) * 100
                return time_seconds, percentage
        except (ValueError, IndexError):
            pass
    elif 'fps=' in line:
        try:
            fps_str = line.split('=')[1].strip()
            # Remove extra text like ' fps'
            fps_str = fps_str.replace(' fps', '').strip()
            fps = float(fps_str)
            return None, fps
        except (ValueError, IndexError):
            pass
    return None, None

def convert_all_mp4s(input_directory=".", output_directory=None):
    """Convert all MP4 files in a directory"""
    
    if output_directory is None:
        output_directory = os.path.join(input_directory, "converted")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Detect best GPU encoder
    gpu_encoder = detect_gpu_encoder()
    
    # Find all MP4 files (prevent duplicates on Windows)
    mp4_files = []
    for pattern in ["*.mp4", "*.MP4"]:
        found_files = glob.glob(os.path.join(input_directory, pattern))
        for file in found_files:
            # Normalize path to prevent duplicates on case-insensitive filesystems
            normalized_path = os.path.normcase(file)
            if not any(os.path.normcase(existing) == normalized_path for existing in mp4_files):
                mp4_files.append(file)
    
    if not mp4_files:
        print("No MP4 files found in the specified directory.")
        return
    
    print(f"Found {len(mp4_files)} MP4 file(s)")
    print(f"Output directory: {output_directory}")
    print("-" * 50)
    
    for i, input_file in enumerate(mp4_files, 1):
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_directory, f"converted_{filename}")
        
        print(f"\n[{i}/{len(mp4_files)}] Processing: {filename}")
        
        # Check if output file already exists
        if os.path.exists(output_file):
            print(f"❌ Output file already exists: {output_file}")
            continue
        
        # Get video information
        width, height, duration = get_video_info(input_file)
        if width is None or height is None:
            print(f"❌ Could not get video information for {filename}")
            continue
            
        print(f"📹 Original resolution: {width}x{height}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        
        # If already 1920x1080, skip
        if width == 1920 and height == 1080:
            print(f"✅ Video already has correct resolution, skipping")
            continue
        
        # Start conversion with GPU encoder
        cmd = convert_video(input_file, output_file, width, height, gpu_encoder)
        
        try:
            print("🔄 Starting conversion...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                universal_newlines=True,
                bufsize=1
            )
            
            current_fps = 0
            last_percentage = 0
            
            # Read progress output with timeout
            import select
            import sys
            
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    break
                
                # Try to read output (non-blocking on Unix, simplified on Windows)
                if sys.platform == "win32":
                    # Windows - simpler approach
                    try:
                        line = process.stdout.readline()
                        if not line:
                            break
                        
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Parse progress
                        time_info, percentage_or_fps = parse_progress(line, duration)
                        
                        if time_info is not None:  # This is time progress
                            percentage = percentage_or_fps
                            if percentage > last_percentage + 1:  # Update every 1%
                                print(f"\r🔄 Progress: {percentage:.1f}% - {current_fps:.1f} fps", end='', flush=True)
                                last_percentage = percentage
                                
                        elif percentage_or_fps is not None:  # This is fps info
                            current_fps = percentage_or_fps
                            
                        # Show general ffmpeg output for debugging
                        if 'frame=' in line or 'time=' in line:
                            # Extract frame and time info from standard ffmpeg output
                            frame_match = re.search(r'frame=\s*(\d+)', line)
                            time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}.\d{2})', line)
                            fps_match = re.search(r'fps=\s*([\d.]+)', line)
                            
                            if time_match and duration > 0:
                                hours, minutes, seconds = time_match.groups()
                                current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                                percentage = (current_time / duration) * 100
                                
                                if fps_match:
                                    try:
                                        current_fps = float(fps_match.group(1))
                                    except ValueError:
                                        pass  # Ignore invalid fps values
                                
                                if percentage > last_percentage + 1 or (percentage - last_percentage) > 5:
                                    print(f"\r🔄 Progress: {percentage:.1f}% - {current_fps:.1f} fps", end='', flush=True)
                                    last_percentage = percentage
                                    
                    except Exception as e:
                        print(f"\nError reading output: {e}")
                        break
                else:
                    # Unix-based systems
                    ready, _, _ = select.select([process.stdout], [], [], 0.1)
                    if ready:
                        line = process.stdout.readline()
                        if not line:
                            break
                        # Same parsing logic as Windows
                        line = line.strip()
                        time_info, percentage_or_fps = parse_progress(line, duration)
                        
                        if time_info is not None:
                            percentage = percentage_or_fps
                            if percentage > last_percentage + 1:
                                print(f"\r🔄 Progress: {percentage:.1f}% - {current_fps:.1f} fps", end='', flush=True)
                                last_percentage = percentage
                        elif percentage_or_fps is not None:
                            current_fps = percentage_or_fps
            
            # Wait for process to finish
            return_code = process.wait()
            
            if return_code == 0:
                print(f"\r✅ Completed: {filename} -> converted_{filename}                    ")
            else:
                print(f"\r❌ Error converting {filename}")
                print(f"Return code: {return_code}")
                # Try to read last output for error info
                try:
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        print(f"Last output: {remaining_output[-200:]}")  # Last 200 chars
                except:
                    pass
                
        except KeyboardInterrupt:
            print(f"\n⚠️  Conversion interrupted by user")
            process.terminate()
            break
        except Exception as e:
            print(f"\r❌ Unexpected error with {filename}: {e}")
    
    print(f"\n{'='*50}")
    print("🎬 All conversions completed!")

if __name__ == "__main__":
    # Configuration
    INPUT_DIR = "."  # Current directory, change to desired directory
    OUTPUT_DIR = None  # None = create 'converted' subdirectory, or specify custom path
    
    print("🎬 MP4 to 1920x1080 Converter with GPU Acceleration")
    print("=" * 50)
    
    # Check if ffmpeg and ffprobe are available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg and/or FFprobe not found!")
        print("Please install FFmpeg first: https://ffmpeg.org/download.html")
        exit(1)
    
    # Start conversion
    convert_all_mp4s(INPUT_DIR, OUTPUT_DIR)