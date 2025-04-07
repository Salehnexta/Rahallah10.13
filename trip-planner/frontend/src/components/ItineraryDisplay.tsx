import React from 'react';

interface ItineraryDisplayProps {
  content: string;
  language: 'en' | 'ar';
}

/**
 * Component to display trip itineraries in a structured, visually appealing format
 * Identifies and formats day-by-day itineraries with activities
 */
const ItineraryDisplay: React.FC<ItineraryDisplayProps> = ({ content, language }) => {
  // Check if content is an itinerary (contains day markers)
  const isItinerary = content.includes('🗓️ Day') || content.includes('🗓️ اليوم');
  
  if (!isItinerary) {
    return <p className="message-text">{content}</p>;
  }
  
  // Parse days from the itinerary content
  const parseItinerary = () => {
    // Split content by days
    const dayRegex = language === 'en' ? /🗓️ Day \d+:/ : /🗓️ اليوم \d+:/;
    const dayParts = content.split(dayRegex).filter(Boolean);
    
    // Extract day numbers
    const dayNumbers = content.match(dayRegex)?.map(day => {
      const match = day.match(/\d+/);
      return match ? parseInt(match[0]) : 0;
    }) || [];
    
    // Skip the first part if it's empty (before the first day marker)
    const startIndex = dayParts[0].trim() === '' ? 1 : 0;
    
    // Map days to their content
    return dayParts.slice(startIndex).map((dayContent, index) => ({
      dayNumber: dayNumbers[index] || index + 1,
      content: dayContent.trim()
    }));
  };
  
  // Parse activities for a day
  const parseActivities = (dayContent: string) => {
    // Activity markers
    const morningMarker = language === 'en' ? '🌅 Morning:' : '🌅 الصباح:';
    const afternoonMarker = language === 'en' ? '🌞 Afternoon:' : '🌞 بعد الظهر:';
    const eveningMarker = language === 'en' ? '🌙 Evening:' : '🌙 المساء:';
    
    // Find activities by time of day
    const morningStart = dayContent.indexOf(morningMarker);
    const afternoonStart = dayContent.indexOf(afternoonMarker);
    const eveningStart = dayContent.indexOf(eveningMarker);
    
    // Extract activity content
    const morning = morningStart !== -1 ? 
      dayContent.substring(
        morningStart + morningMarker.length, 
        afternoonStart !== -1 ? afternoonStart : (eveningStart !== -1 ? eveningStart : dayContent.length)
      ).trim() : '';
      
    const afternoon = afternoonStart !== -1 ? 
      dayContent.substring(
        afternoonStart + afternoonMarker.length, 
        eveningStart !== -1 ? eveningStart : dayContent.length
      ).trim() : '';
    
    const evening = eveningStart !== -1 ? 
      dayContent.substring(eveningStart + eveningMarker.length).trim() : '';
    
    return {
      morning,
      afternoon,
      evening
    };
  };
  
  const days = parseItinerary();
  
  return (
    <div className={`itinerary-container ${language === 'ar' ? 'rtl' : 'ltr'}`}>
      {days.map((day) => {
        const activities = parseActivities(day.content);
        return (
          <div key={day.dayNumber} className="itinerary-day">
            <h3 className="day-title">
              {language === 'en' ? `Day ${day.dayNumber}` : `اليوم ${day.dayNumber}`}
            </h3>
            <div className="day-activities">
              {activities.morning && (
                <div className="activity morning">
                  <div className="activity-icon">🌅</div>
                  <div className="activity-content">
                    <h4>{language === 'en' ? 'Morning' : 'الصباح'}</h4>
                    <p>{activities.morning}</p>
                  </div>
                </div>
              )}
              
              {activities.afternoon && (
                <div className="activity afternoon">
                  <div className="activity-icon">🌞</div>
                  <div className="activity-content">
                    <h4>{language === 'en' ? 'Afternoon' : 'بعد الظهر'}</h4>
                    <p>{activities.afternoon}</p>
                  </div>
                </div>
              )}
              
              {activities.evening && (
                <div className="activity evening">
                  <div className="activity-icon">🌙</div>
                  <div className="activity-content">
                    <h4>{language === 'en' ? 'Evening' : 'المساء'}</h4>
                    <p>{activities.evening}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ItineraryDisplay;
