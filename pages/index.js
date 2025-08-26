import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [stories, setStories] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [swipeHint, setSwipeHint] = useState(true);

  useEffect(() => {
    // Load sample data for now
    const sampleStories = [
      {
        type: 'opening',
        date: 'MONDAY, AUGUST 25, 2025',
        headline: 'Good morning, typhoon chaos hits Asia\'s coastal millions',
        readingTime: '2 minute read'
      },
      {
        type: 'news',
        number: 1,
        emoji: '🌀',
        title: 'Massive Typhoon Forces Vietnam and China Emergency Evacuations',
        summary: 'Typhoon Kajiki threatens millions as Vietnam evacuates 586,000 people and cancels flights. China\'s resort city Sanya closed businesses and public transport.',
        url: 'https://reuters.com/typhoon'
      },
      {
        type: 'news',
        number: 2,
        emoji: '☕',
        title: 'Coffee Giants Near Record $18 Billion Merger Deal',
        summary: 'Keurig Dr Pepper is close to buying Dutch company JDE Peet\'s for $18 billion. This merger would create a global coffee powerhouse.',
        url: 'https://bloomberg.com/coffee'
      },
      {
        type: 'news',
        number: 3,
        emoji: '🌾',
        title: 'Brazil Farm Bankruptcies Surge Threatening Global Food Supply',
        summary: 'Brazil\'s agricultural sector faces crisis with farm bankruptcies jumping 138% to 1,272 cases in 2024.',
        url: 'https://reuters.com/brazil'
      },
      {
        type: 'news',
        number: 4,
        emoji: '🤖',
        title: 'UK Government Considers Free ChatGPT Plus for All Citizens',
        summary: 'Minister Peter Kyle discussed a £2 billion deal with OpenAI\'s Sam Altman to provide ChatGPT Plus to all 67 million UK residents.',
        url: 'https://bbc.com/uk-ai'
      },
      {
        type: 'news',
        number: 5,
        emoji: '🚀',
        title: 'NASA Discovers Earth-Like Planet With Water Signatures',
        summary: 'James Webb telescope identifies potentially habitable exoplanet just 40 light-years away.',
        url: 'https://nasa.gov/exoplanet'
      },
      {
        type: 'news',
        number: 6,
        emoji: '📈',
        title: 'Tech Stocks Drive S&P 500 to All-Time Record High',
        summary: 'Markets surge as artificial intelligence companies lead unprecedented rally.',
        url: 'https://cnbc.com/markets'
      },
      {
        type: 'news',
        number: 7,
        emoji: '🏅',
        title: 'Paris Olympics Shatters All Previous Attendance Records',
        summary: 'Summer games attract record-breaking 15 million spectators across innovative urban venues.',
        url: 'https://olympics.com/paris'
      },
      {
        type: 'news',
        number: 8,
        emoji: '🎬',
        title: 'Disney Launches Major Offensive in Streaming Wars',
        summary: 'Entertainment giant announces $50 billion content investment and new pricing strategy.',
        url: 'https://variety.com/disney'
      },
      {
        type: 'news',
        number: 9,
        emoji: '🧬',
        title: 'Revolutionary Cancer Treatment Shows 90% Success Rate',
        summary: 'New immunotherapy approach demonstrates unprecedented results in late-stage clinical trials.',
        url: 'https://nature.com/cancer'
      },
      {
        type: 'news',
        number: 10,
        emoji: '🌍',
        title: 'Breakthrough Carbon Capture Technology Promises Net Zero',
        summary: 'Scientists unveil revolutionary atmospheric carbon removal system with 99% efficiency rate.',
        url: 'https://science.org/climate'
      },
      {
        type: 'history',
        content: `
          <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 48px; font-weight: 800; margin-bottom: 40px;">Today in History</h1>
            <div style="max-width: 600px; margin: 0 auto; text-align: left;">
              <div style="display: flex; gap: 24px; margin-bottom: 24px; align-items: center;">
                <span style="padding: 8px 16px; background: #C6E5F3; color: #007AFF; border-radius: 100px; font-weight: 700;">1991</span>
                <span style="font-size: 18px;">Linux operating system released by Linus Torvalds</span>
              </div>
              <div style="display: flex; gap: 24px; margin-bottom: 24px; align-items: center;">
                <span style="padding: 8px 16px; background: #C6E5F3; color: #007AFF; border-radius: 100px; font-weight: 700;">1944</span>
                <span style="font-size: 18px;">Paris liberated from Nazi occupation during World War II</span>
              </div>
              <div style="display: flex; gap: 24px; margin-bottom: 24px; align-items: center;">
                <span style="padding: 8px 16px; background: #C6E5F3; color: #007AFF; border-radius: 100px; font-weight: 700;">1835</span>
                <span style="font-size: 18px;">New York Sun publishes Great Moon Hoax articles</span>
              </div>
              <div style="display: flex; gap: 24px; margin-bottom: 24px; align-items: center;">
                <span style="padding: 8px 16px; background: #C6E5F3; color: #007AFF; border-radius: 100px; font-weight: 700;">1609</span>
                <span style="font-size: 18px;">Galileo demonstrates his first telescope to Venetian lawmakers</span>
              </div>
            </div>
          </div>
        `
      },
      {
        type: 'end',
        content: `
          <div style="text-align: center;">
            <div style="font-size: 64px; margin-bottom: 32px;">👋</div>
            <h2 style="font-size: 36px; font-weight: 700; margin-bottom: 16px;">That's all for today, see you tomorrow :)</h2>
            <p style="font-size: 17px; color: #86868b;">Stay informed with Ten News</p>
          </div>
        `
      },
      {
        type: 'newsletter',
        content: `
          <div style="background: #000; color: #fff; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 24px;">
            <h2 style="font-size: 42px; font-weight: 700; margin-bottom: 24px;">Get Ten News Daily</h2>
            <p style="font-size: 18px; color: #86868b; margin-bottom: 48px;">The day's top stories, delivered to your inbox</p>
            <div style="width: 100%; max-width: 400px;">
              <input type="email" placeholder="Email" style="width: 100%; padding: 18px 24px; font-size: 17px; border: none; border-radius: 12px; background: #1c1c1e; color: #fff; margin-bottom: 16px;" />
              <button style="width: 100%; padding: 18px 40px; background: #fff; color: #000; border: none; border-radius: 12px; font-size: 18px; font-weight: 600; cursor: pointer;">Subscribe</button>
            </div>
            <div style="position: absolute; bottom: 40px; font-size: 15px; color: #6e6e73;">tennews.ai</div>
          </div>
        `
      }
    ];
    
    setStories(sampleStories);
    setLoading(false);
  }, []);

  const goToStory = (index) => {
    if (index >= 0 && index < stories.length) {
      setCurrentIndex(index);
      if (index > 0) setSwipeHint(false);
    }
  };

  const nextStory = () => goToStory(currentIndex + 1);
  const prevStory = () => goToStory(currentIndex - 1);

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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#fff', color: '#000' }}>
        <div style={{ fontSize: '24px' }}>Loading news...</div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Ten News</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <style>{`
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
        `}</style>
      </Head>
      
      <div style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}>
        {/* Header */}
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '52px',
          background: 'rgba(255,255,255,0.94)',
          backdropFilter: 'blur(20px)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          borderBottom: '0.5px solid rgba(0,0,0,0.08)'
        }}>
          <div style={{ fontSize: '15px', fontWeight: 500, color: '#86868b' }}>Monday, Aug 25</div>
          <div style={{ fontSize: '17px', fontWeight: 600, color: '#1d1d1f' }}>Ten News</div>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'linear-gradient(135deg, #007AFF, #5856D6)' }}></div>
        </div>

        {/* Stories */}
        {stories.map((story, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '120px 24px 80px',
              background: story.type === 'newsletter' ? '#000' : '#fff',
              transform: `translateY(${index === currentIndex ? '0' : index < currentIndex ? '-100%' : '100%'})`,
              transition: 'transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
              zIndex: index === currentIndex ? 10 : 1,
              cursor: story.url ? 'pointer' : 'default'
            }}
            onClick={() => story.url && window.open(story.url, '_blank')}
          >
            <div style={{ maxWidth: '680px', width: '100%', margin: '0 auto' }}>
              {story.type === 'opening' ? (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '1px', color: '#FF3B30', textTransform: 'uppercase', marginBottom: '32px' }}>
                    {story.date}
                  </div>
                  <h1 style={{ fontSize: '56px', fontWeight: 800, lineHeight: 1.05, letterSpacing: '-2px', marginBottom: '40px' }}>
                    {story.headline}
                  </h1>
                  <span style={{ display: 'inline-block', padding: '12px 24px', background: '#C6E5F3', color: '#007AFF', borderRadius: '980px', fontSize: '17px', fontWeight: 500 }}>
                    {story.readingTime}
                  </span>
                </div>
              ) : story.type === 'news' ? (
                <>
                  <div style={{ display: 'inline-block', width: '40px', height: '40px', background: '#f5f5f7', borderRadius: '12px', textAlign: 'center', lineHeight: '40px', fontSize: '18px', fontWeight: 600, color: '#86868b', marginBottom: '24px' }}>
                    {story.number}
                  </div>
                  <h1 style={{ fontSize: '44px', fontWeight: 700, lineHeight: 1.08, letterSpacing: '-1.2px', marginBottom: '24px', textAlign: 'left' }}>
                    {story.emoji} {story.title}
                  </h1>
                  <p style={{ fontSize: '21px', lineHeight: 1.45, letterSpacing: '-0.3px', textAlign: 'left' }}>
                    {story.summary}
                  </p>
                </>
              ) : (
                <div dangerouslySetInnerHTML={{ __html: story.content }} />
              )}
            </div>
          </div>
        ))}

        {/* Progress Dots */}
        <div style={{
          position: 'fixed',
          bottom: '32px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '8px',
          zIndex: 100
        }}>
          {stories.map((_, index) => (
            <div
              key={index}
              onClick={() => goToStory(index)}
              style={{
                width: index === currentIndex ? '28px' : '6px',
                height: '6px',
                borderRadius: '3px',
                background: index === currentIndex ? '#1d1d1f' : '#d2d2d7',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
            />
          ))}
        </div>

        {/* Swipe Hint */}
        {swipeHint && (
          <div style={{
            position: 'fixed',
            bottom: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            fontSize: '13px',
            color: '#86868b',
            opacity: 0.6
          }}>
            Swipe up for next story
          </div>
        )}
      </div>
    </>
  );
}
