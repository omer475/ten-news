import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [stories, setStories] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [swipeHint, setSwipeHint] = useState(true);

  useEffect(() => {
    // Fetch news from your API
    fetch('/api/news')
      .then(res => res.json())
      .then(data => {
        setStories(data.stories);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading news:', err);
        setLoading(false);
      });
  }, []);

  const goToStory = (index) => {
    if (index >= 0 && index < stories.length) {
      setCurrentIndex(index);
      if (index > 0) setSwipeHint(false);
    }
  };

  const nextStory = () => goToStory(currentIndex + 1);
  const prevStory = () => goToStory(currentIndex - 1);

  // Touch handling
  useEffect(() => {
    let startY = 0;

    const handleTouchStart = (e) => {
      startY = e.touches[0].clientY;
    };

    const handleTouchEnd = (e) => {
      const endY = e.changedTouches[0].clientY;
      const diff = startY - endY;
      
      if (Math.abs(diff) > 50) {
        if (diff > 0) nextStory();
        else prevStory();
      }
    };

    const handleWheel = (e) => {
      e.preventDefault();
      if (e.deltaY > 0) nextStory();
      else prevStory();
    };

    const handleKeyDown = (e) => {
      if (e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        nextStory();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        prevStory();
      }
    };

    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);
    document.addEventListener('wheel', handleWheel, { passive: false });
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
      document.removeEventListener('wheel', handleWheel);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentIndex, stories.length]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#000', color: '#fff' }}>
        <div style={{ fontSize: '24px' }}>Loading news...</div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Ten News</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
      </Head>
      
      <div className="app">
        <style jsx global>{`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
            background: #ffffff;
            color: #1d1d1f;
            overflow: hidden;
            position: fixed;
            width: 100%;
            height: 100%;
            touch-action: none;
          }

          .app {
            position: relative;
            width: 100%;
            height: 100%;
            overflow: hidden;
          }

          .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 52px;
            background: rgba(255,255,255,0.94);
            backdrop-filter: blur(20px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            border-bottom: 0.5px solid rgba(0,0,0,0.08);
          }

          .date-label {
            font-size: 15px;
            font-weight: 500;
            color: #86868b;
          }

          .logo {
            font-size: 17px;
            font-weight: 600;
            color: #1d1d1f;
          }

          .profile-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: linear-gradient(135deg, #007AFF, #5856D6);
          }

          .story {
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 120px 24px 80px;
            background: #ffffff;
            cursor: pointer;
            transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          }

          .story.active {
            transform: translateY(0);
            z-index: 10;
          }

          .story.next {
            transform: translateY(100%);
          }

          .story.prev {
            transform: translateY(-100%);
          }

          .content-wrapper {
            max-width: 680px;
            width: 100%;
            margin: 0 auto;
          }

          .article-number-box {
            display: inline-block;
            width: 40px;
            height: 40px;
            background: #f5f5f7;
            border-radius: 12px;
            text-align: center;
            line-height: 40px;
            font-size: 18px;
            font-weight: 600;
            color: #86868b;
            margin-bottom: 24px;
          }

          .headline {
            font-size: 44px;
            font-weight: 700;
            line-height: 1.08;
            letter-spacing: -1.2px;
            color: #1d1d1f;
            margin-bottom: 24px;
            text-align: left;
          }

          .summary {
            font-size: 21px;
            line-height: 1.45;
            letter-spacing: -0.3px;
            color: #1d1d1f;
            text-align: left;
          }

          .opening-card {
            text-align: center;
          }

          .date-header {
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            color: #FF3B30;
            text-transform: uppercase;
            margin-bottom: 32px;
          }

          .opening-headline {
            font-size: 56px;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -2px;
            color: #1d1d1f;
            margin-bottom: 40px;
          }

          .opening-time {
            display: inline-block;
            padding: 12px 24px;
            background: #C6E5F3;
            color: #007AFF;
            border-radius: 980px;
            font-size: 17px;
            font-weight: 500;
          }

          .progress-dots {
            position: fixed;
            bottom: 32px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
            z-index: 100;
          }

          .dot {
            width: 6px;
            height: 6px;
            border-radius: 3px;
            background: #d2d2d7;
            cursor: pointer;
            transition: all 0.3s ease;
          }

          .dot.active {
            width: 28px;
            background: #1d1d1f;
          }

          .swipe-hint {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 13px;
            color: #86868b;
            opacity: ${swipeHint ? 0.6 : 0};
            transition: opacity 0.3s ease;
            pointer-events: none;
          }

          @media (max-width: 768px) {
            .headline {
              font-size: 34px;
            }
            .summary {
              font-size: 18px;
            }
            .opening-headline {
              font-size: 42px;
            }
          }
        `}</style>

        {/* Header */}
        <div className="header">
          <div className="date-label">Monday, Aug 25</div>
          <div className="logo">Ten News</div>
          <div className="profile-icon"></div>
        </div>

        {/* Stories */}
        <div className="stories-container">
          {stories.map((story, index) => (
            <div
              key={index}
              className={`story ${index === currentIndex ? 'active' : index < currentIndex ? 'prev' : 'next'}`}
              onClick={() => {
                if (story.url && index !== 0 && index !== 10 && index !== 11 && index !== 12) {
                  window.open(story.url, '_blank');
                }
              }}
            >
              <div className={`content-wrapper ${story.type === 'opening' ? 'opening-card' : ''}`}>
                {story.type === 'opening' ? (
                  <>
                    <div className="date-header">{story.date}</div>
                    <h1 className="opening-headline">{story.headline}</h1>
                    <span className="opening-time">{story.readingTime}</span>
                  </>
                ) : story.type === 'news' ? (
                  <>
                    <div className="article-number-box">{story.number}</div>
                    <h1 className="headline">{story.emoji} {story.title}</h1>
                    <p className="summary">{story.summary}</p>
                  </>
                ) : (
                  <div dangerouslySetInnerHTML={{ __html: story.content }} />
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Progress Dots */}
        <div className="progress-dots">
          {stories.map((_, index) => (
            <div
              key={index}
              className={`dot ${index === currentIndex ? 'active' : ''}`}
              onClick={() => goToStory(index)}
            />
          ))}
        </div>

        {/* Swipe Hint */}
        <div className="swipe-hint">Swipe up for next story</div>
      </div>
    </>
  );
}
