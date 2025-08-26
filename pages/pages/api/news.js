export default async function handler(req, res) {
  // For now, return sample data
  // Later we'll connect your Python script here
  
  const stories = [
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
      summary: 'Typhoon Kajiki threatens millions as Vietnam evacuates 586,000 people and cancels flights. China\'s resort city Sanya closed businesses and public transport. The powerful storm will hit south China or central Vietnam soon.',
      url: 'https://example.com/typhoon'
    },
    {
      type: 'news',
      number: 2,
      emoji: '☕',
      title: 'Coffee Giants Near Record $18 Billion Merger Deal',
      summary: 'Keurig Dr Pepper is close to buying Dutch company JDE Peet\'s for $18 billion. This merger would create a global coffee powerhouse, combining brands like Keurig pods with European coffee labels.',
      url: 'https://example.com/coffee'
    },
    // Add all 10 news items here
    {
      type: 'html',
      content: '<div style="text-align: center;"><h1 style="font-size: 48px; font-weight: 800;">Today in History</h1><!-- Add history content --></div>'
    },
    {
      type: 'html',
      content: '<div style="text-align: center;"><div style="font-size: 64px;">👋</div><h2>That\'s all for today, see you tomorrow :)</h2></div>'
    }
  ];

  res.status(200).json({ stories });
}
