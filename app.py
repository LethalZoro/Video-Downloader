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
    // Auto-scroll functionality with improved detection
    let scrollTimeout;
    let isAutoScrollEnabled = true;
    
    function smoothScrollToBottom() {
        if (!isAutoScrollEnabled) return;
        
        // Clear any pending scroll
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(function() {
            const maxScroll = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
            
            window.scrollTo({
                top: maxScroll,
                behavior: 'smooth'
            });
        }, 100);
    }
    
    // More aggressive content detection
    function setupAutoScroll() {
        // Use multiple observers for better detection
        const targetNode = document.querySelector('.main') || document.body;
        
        const observer = new MutationObserver(function(mutations) {
            let hasNewContent = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // More comprehensive content detection
                            if (node.tagName === 'DIV' || 
                                node.querySelector && (
                                    node.querySelector('.stMarkdown') ||
                                    node.querySelector('.stProgress') ||
                                    node.querySelector('.stSpinner') ||
                                    node.querySelector('.stAlert') ||
                                    node.querySelector('.stSuccess') ||
                                    node.querySelector('.stError') ||
                                    node.querySelector('.stWarning') ||
                                    node.querySelector('.stInfo') ||
                                    node.querySelector('[data-testid]') ||
                                    node.querySelector('.element-container')
                                )) {
                                hasNewContent = true;
                            }
                        }
                    });
                }
            });
            
            if (hasNewContent) {
                smoothScrollToBottom();
            }
        });
        
        observer.observe(targetNode, {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false
        });
        
        // Also observe attribute changes that might indicate content updates
        const attrObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
                    smoothScrollToBottom();
                }
            });
        });
        
        attrObserver.observe(targetNode, {
            attributes: true,
            subtree: true,
            attributeFilter: ['style', 'class']
        });
        
        // Periodic scroll check for missed content
        setInterval(function() {
            const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
            
            // If we're not at the bottom and should be, scroll down
            if (maxScroll - currentScroll > 50) {
                smoothScrollToBottom();
            }
        }, 1000);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupAutoScroll);
    } else {
        setupAutoScroll();
    }
    
    // Backup initialization
    setTimeout(setupAutoScroll, 500);
    setTimeout(setupAutoScroll, 2000);
    
    // Force scroll function for manual triggering
    window.forceScrollToBottom = function() {
        setTimeout(function() {
            const maxScroll = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight
            );
            window.scrollTo({
                top: maxScroll,
                behavior: 'smooth'
            });
        }, 100);
    };
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
                        
                        # Trigger auto-scroll to show video details
                        st.markdown("""
                            <script>
                            // Multiple fallback scroll triggers
                            setTimeout(function() {
                                if (typeof smoothScrollToBottom === 'function') {
                                    smoothScrollToBottom();
                                } else if (typeof window.forceScrollToBottom === 'function') {
                                    window.forceScrollToBottom();
                                } else {
                                    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
                                }
                            }, 200);
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
                        
                        # Trigger auto-scroll to download section
                        st.markdown("""
                            <script>
                            setTimeout(function() {
                                if (typeof smoothScrollToBottom === 'function') {
                                    smoothScrollToBottom();
                                } else if (typeof window.forceScrollToBottom === 'function') {
                                    window.forceScrollToBottom();
                                } else {
                                    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
                                }
                            }, 300);
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
                                
                                # Trigger auto-scroll to completion section
                                st.markdown("""
                                    <script>
                                    setTimeout(function() {
                                        if (typeof smoothScrollToBottom === 'function') {
                                            smoothScrollToBottom();
                                        } else if (typeof window.forceScrollToBottom === 'function') {
                                            window.forceScrollToBottom();
                                        } else {
                                            window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
                                        }
                                    }, 400);
                                    </script>
                                """, unsafe_allow_html=True)
                                
                                # File info section
                                full_path = os.path.abspath(video_file)
                                file_name = os.path.basename(video_file)
                                file_size = os.path.getsize(video_file)
                                file_size_mb = file_size / (1024 * 1024)
                                
                                # Read file and prepare download data
                                with open(video_file, "rb") as file:
                                    file_data = file.read()
                                
                                import base64
                                b64_data = base64.b64encode(file_data).decode()
                                
                                # Success section with download functionality
                                st.markdown(f"""
                                    <div style="text-align: center;">
                                        <a id="download-link" 
                                           href="data:video/mp4;base64,{b64_data}" 
                                           download="{file_name}"
                                           style="display: block; text-decoration: none;">
                                            <div class="success-box" style="cursor: pointer; transition: transform 0.2s;">
                                                <h3>🎉 File Processed!</h3>
                                                <p>Your file has been processed. Click to download.</p>
                                                <p style="margin-top: 1rem; font-size: 0.9rem;">
                                                    📄 {file_name} | 📏 {file_size_mb:.2f} MB
                                                </p>
                                            </div>
                                        </a>
                                    </div>
                                    <script>
                                        // Auto-download after a short delay
                                        setTimeout(function() {{
                                            document.getElementById('download-link').click();
                                        }}, 800);
                                        // Trigger final scroll to bottom with multiple fallbacks
                                        setTimeout(function() {{
                                            if (typeof smoothScrollToBottom === 'function') {{
                                                smoothScrollToBottom();
                                            }} else if (typeof window.forceScrollToBottom === 'function') {{
                                                window.forceScrollToBottom();
                                            }} else {{
                                                window.scrollTo({{top: document.body.scrollHeight, behavior: 'smooth'}});
                                            }}
                                        }}, 500);
                                        
                                        // Add hover effect
                                        document.querySelector('.success-box').addEventListener('mouseenter', function() {{
                                            this.style.transform = 'scale(1.02)';
                                        }});
                                        document.querySelector('.success-box').addEventListener('mouseleave', function() {{
                                            this.style.transform = 'scale(1)';
                                        }});
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
