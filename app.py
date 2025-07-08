import streamlit as st
import yt_dlp
import os
import re

def get_video_info(url):
    """
    Gets video information using yt-dlp.
    """
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict
        except yt_dlp.utils.DownloadError as e:
            st.error(f"Error extracting video info: {e}")
            return None

def download_video(url, download_path='.'):
    """
    Downloads a video from the given URL using yt-dlp.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # st.info("Starting download...")
            ydl.download([url])
            return ydl.prepare_filename(ydl.extract_info(url, download=False))
        except yt_dlp.utils.DownloadError as e:
            st.error(f"Error downloading video: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None

def progress_hook(d):
    """
    Hook for yt-dlp to show download progress in Streamlit.
    """
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        if total_bytes:
            progress = (d['downloaded_bytes'] / total_bytes) * 100
            # Create a progress bar that updates
            if not hasattr(st.session_state, 'progress_bar'):
                st.session_state.progress_bar = st.progress(0)
            st.session_state.progress_bar.progress(progress / 100)
            
            # Show download speed and ETA if available
            speed = d.get('speed')
            eta = d.get('eta')
            if speed and eta:
                st.info(f"Speed: {speed/1024/1024:.1f} MB/s | ETA: {eta}s | Progress: {progress:.1f}%")
    elif d['status'] == 'finished':
        if hasattr(st.session_state, 'progress_bar'):
            st.session_state.progress_bar.progress(1.0)
        # st.success("✅ Download complete!")


def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="Video Downloader", 
        layout="wide",
        page_icon="🎬",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #ff4b4b;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .url-input {
        margin: 2rem 0;
    }
    .button-container {
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    .path-display {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        font-family: monospace;
        word-break: break-all;
        color: #333;
        font-weight: bold;
    }
    .location-label {
        color: white;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Fixed footer styles */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        # background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 999;
        padding: 0.5rem 0;
    }
    
    /* Add bottom padding to main content to prevent footer overlap */
    .main .block-container {
        padding-bottom: 60px;
    }
    </style>
    
    <script>
    // Auto-scroll functionality
    function smoothScrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Observer to detect new content being added
    function setupAutoScroll() {
        const observer = new MutationObserver(function(mutations) {
            let shouldScroll = false;
            
            mutations.forEach(function(mutation) {
                // Check if new nodes were added
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if any added node contains significant content
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Look for Streamlit content containers
                            if (node.querySelector('.stMarkdown, .stProgress, .stSpinner, .stSuccess, .stError, .stWarning, .stInfo') ||
                                node.classList.contains('stMarkdown') ||
                                node.classList.contains('stProgress') ||
                                node.classList.contains('stSpinner') ||
                                node.classList.contains('stSuccess') ||
                                node.classList.contains('stError') ||
                                node.classList.contains('stWarning') ||
                                node.classList.contains('stInfo')) {
                                shouldScroll = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldScroll) {
                // Small delay to ensure content is rendered
                setTimeout(smoothScrollToBottom, 100);
            }
        });
        
        // Start observing the document body for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Also scroll when window is resized (mobile orientation change, etc.)
        window.addEventListener('resize', function() {
            setTimeout(smoothScrollToBottom, 300);
        });
    }
    
    // Initialize auto-scroll when page loads
    document.addEventListener('DOMContentLoaded', setupAutoScroll);
    
    // Also setup auto-scroll after a delay in case DOM was already loaded
    setTimeout(setupAutoScroll, 500);
    </script>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown('<h1 class="main-header">🎬 Video Downloader Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Download videos from YouTube, Instagram, TikTok and more platforms</p>', unsafe_allow_html=True)
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Create a form for URL input with Enter key support
        with st.form(key="video_download_form", clear_on_submit=False):
            st.markdown('<div class="url-input">', unsafe_allow_html=True)
            video_url = st.text_input(
                "🔗 Enter video URL:",
                placeholder="Paste your video URL here (YouTube, Instagram, TikTok...)",
                help="Supports most video platforms including YouTube, Instagram, TikTok, and more",
                key="video_url_input"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Form submit button (single button for download)
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            
            download_button = st.form_submit_button(
                "⬇️ Download Video", 
                use_container_width=True,
                type="primary",
                help="Download the video to your device (or press Enter)"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    if download_button:
        if video_url:
            # Keep everything in the same centered container
            with col2:
                # First fetch video info
                with st.spinner("🔍 Fetching video information..."):
                    info = get_video_info(video_url)
                    if info:
                        st.subheader("📹 Video Details")
                        
                        # Auto-scroll to show video details
                        st.markdown("""
                            <script>
                            setTimeout(function() {
                                window.scrollTo({
                                    top: document.body.scrollHeight,
                                    behavior: 'smooth'
                                });
                            }, 300);
                            </script>
                        """, unsafe_allow_html=True)
                        
                        # Create columns for better layout
                        info_col1, info_col2 = st.columns([2, 1])
                        
                        with info_col1:
                            st.markdown(f"**🎬 Title:** {info.get('title', 'N/A')}")
                            st.markdown(f"**👤 Uploader:** {info.get('uploader', 'N/A')}")
                            st.markdown(f"**⏱️ Duration:** {info.get('duration_string', 'N/A')}")
                            st.markdown(f"**👀 Views:** {info.get('view_count', 'N/A'):,}" if info.get('view_count') else "**👀 Views:** N/A")
                        
                        with info_col2:
                            if info.get('thumbnail'):
                                st.image(info.get('thumbnail'), caption="Video Thumbnail", use_container_width=True)
                        
                        st.markdown("---")  # Simple divider
                        st.subheader("⬇️ Downloading Video...")
                        
                        # Auto-scroll to download section
                        st.markdown("""
                            <script>
                            setTimeout(function() {
                                window.scrollTo({
                                    top: document.body.scrollHeight,
                                    behavior: 'smooth'
                                });
                            }, 500);
                            </script>
                        """, unsafe_allow_html=True)
                        
                        # Then proceed with download
                        with st.spinner("📥 Downloading video..."):
                            download_path = "."
                            
                            # Initialize progress tracking
                            if 'progress_bar' in st.session_state:
                                del st.session_state.progress_bar
                            
                            # Create progress placeholder
                            progress_placeholder = st.empty()
                            with progress_placeholder.container():
                                # st.info("Initializing download...")
                                st.session_state.progress_bar = st.progress(0)
                            
                            video_file = download_video(video_url, download_path)
                            if video_file and os.path.exists(video_file):
                                
                                # Success section
                                st.markdown("""
                                    <div class="success-box">
                                        <h3>🎉 Download Complete!</h3>
                                        <p>Your video has been successfully downloaded and is ready!</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Auto-scroll to completion section
                                st.markdown("""
                                    <script>
                                    setTimeout(function() {
                                        window.scrollTo({
                                            top: document.body.scrollHeight,
                                            behavior: 'smooth'
                                        });
                                    }, 600);
                                    </script>
                                """, unsafe_allow_html=True)
                                
                                # File info section
                                full_path = os.path.abspath(video_file)
                                file_name = os.path.basename(video_file)
                                file_size = os.path.getsize(video_file)
                                file_size_mb = file_size / (1024 * 1024)
                                
                                st.markdown("### 📁 File Information")
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.markdown(f"**📄 Filename:** `{file_name}`")
                                    st.markdown(f"**📏 File Size:** `{file_size_mb:.2f} MB`")
                                
                                with col_info2:
                                    st.markdown('<div class="location-label">📍 Location:</div>', unsafe_allow_html=True)
                                    st.markdown(f'<div class="path-display">{full_path}</div>', unsafe_allow_html=True)
                                
                                # File actions with JavaScript (no page refresh)
                                folder_path = os.path.dirname(full_path)
                                
                                
                                # Download buttons section
                                st.markdown("### 💾 Download Options")
                                
                                # Read file and create download button with auto-download
                                with open(video_file, "rb") as file:
                                    file_data = file.read()
                                
                                # Create single download button (no page rerun)
                                import base64
                                b64_data = base64.b64encode(file_data).decode()
                                
                                st.markdown(f"""
                                    <div style="text-align: center;">
                                        <a id="download-link" 
                                           href="data:video/mp4;base64,{b64_data}" 
                                           download="{file_name}"
                                           style="display: inline-block; padding: 0.75rem 1.5rem; 
                                                  background: linear-gradient(135deg, #ff4b4b, #ff6b6b); 
                                                  color: white; text-decoration: none; border-radius: 8px; 
                                                  font-weight: bold; box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
                                                  width: 100%;">
                                            🔄 Download
                                        </a>
                                    </div>
                                    <script>
                                        // Auto-download after a short delay
                                        setTimeout(function() {{
                                            document.getElementById('download-link').click();
                                        }}, 800);
                                        // Scroll to bottom
                                        setTimeout(function() {{
                                            window.scrollTo(0, document.body.scrollHeight);
                                        }}, 200);
                                    </script>
                                """, unsafe_allow_html=True)
                            else:
                                st.error("❌ Download failed. Please try again.")
                    else:
                        st.error("❌ Failed to fetch video information. Please check the URL and try again.")
        else:
            with col2:
                st.warning("⚠️ Please enter a video URL first!")

    # Fixed footer section
    st.markdown("""
        <div class="footer">
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 0.85rem; color: white;">
                    Made with ❤️ by a <a href="https://www.saliklabs.com/" target="_blank" 
                    style="color: #ff4b4b; text-decoration: none; font-weight: bold;">Salik Labs</a> developer
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
