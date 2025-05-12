# Social Triggers Design for Grace

## Overview
This document outlines the design for Grace's social triggers system, which will enable dynamic detection of conversation patterns that should prompt social media searches and data retrieval. The system will help Grace understand when to prioritize using Nitter for gathering social media information based on contextual cues in user conversations.

## Social Trigger Mechanisms

### 1. Pattern Detection Framework
- **Purpose**: Automatically identify when social media information would be valuable
- **Implementation**: Pattern matching against conversation context
- **Integration**: Works with conversation management system to analyze user inputs
- **Priority**: Determines when social searches should take precedence over other actions

### 2. Trigger Categories

#### User Mention Detection
- **Pattern**: References to usernames with @ symbol
- **Example Triggers**: "@username", "check what @person said"
- **Action**: Retrieve recent tweets or profile information for mentioned user
- **Implementation**: Regex pattern matching for @username format

#### Trend Detection
- **Pattern**: Keywords related to trending topics
- **Example Triggers**: "trending", "viral", "popular", "what's hot"
- **Action**: Retrieve current trending topics or trending content for specific topics
- **Implementation**: Keyword matching with context analysis

#### News Monitoring
- **Pattern**: Requests for recent information or updates
- **Example Triggers**: "news", "latest", "updates", "recent developments"
- **Action**: Retrieve recent news-related tweets about specified topics
- **Implementation**: Keyword matching with recency analysis

#### Company Tracking
- **Pattern**: Mentions of major tech companies or crypto projects
- **Example Triggers**: "Google", "Apple", "Microsoft", "Twitter", "X", "Meta", "Facebook", "Amazon", "Bitcoin", "Ethereum", "Solana"
- **Action**: Retrieve recent information about mentioned companies
- **Implementation**: Entity recognition with company name database

#### Recommendation Requests
- **Pattern**: Requests for suggestions or similar items
- **Example Triggers**: "recommend", "suggest", "similar to", "like", "alternative"
- **Action**: Retrieve popular opinions or recommendations on specified topics
- **Implementation**: Intent recognition for recommendation requests

### 3. Contextual Awareness

#### Topic Relevance Assessment
- **Purpose**: Determine if social information would be relevant to current topic
- **Implementation**: Topic modeling to assess relevance of social data
- **Scoring**: Relevance score to determine priority of social search

#### User Interest Profiling
- **Purpose**: Track user's interest in social information
- **Implementation**: User-specific tracking of social trigger responses
- **Adaptation**: Adjust trigger sensitivity based on user preferences

#### Conversation Flow Analysis
- **Purpose**: Determine appropriate timing for social information
- **Implementation**: Conversation state tracking
- **Timing**: Identify natural points to introduce social information

## Integration with Memory System

### 1. Trigger Storage
- **Short-Term Memory**: Active triggers relevant to current conversation
- **Medium-Term Memory**: User-specific trigger preferences
- **Long-Term Memory**: Common trigger patterns and effectiveness

### 2. Trigger-Memory Bridging
- **Pattern Recognition**: Links detected patterns to memory retrieval
- **Context Enhancement**: Uses memory to enhance trigger detection
- **Learning Mechanism**: Improves trigger detection based on past effectiveness

## Integration with Nitter Service

### 1. Trigger-to-Query Mapping
- **Purpose**: Convert detected triggers to effective Nitter queries
- **Implementation**: Query formulation based on trigger type
- **Optimization**: Refine queries based on result quality

### 2. Function Selection
- **get_tweets()**: For trend detection, news monitoring, and general searches
- **get_tweet_by_id()**: For specific tweet references
- **get_profile_info()**: For user mention triggers
- **_make_request()**: For custom query needs

### 3. Result Processing
- **Filtering**: Remove irrelevant or low-quality results
- **Ranking**: Prioritize results based on relevance to trigger
- **Summarization**: Condense information for presentation
- **Memory Storage**: Store valuable results in appropriate memory level

## Implementation Approach

### 1. Trigger Detection System
```python
class SocialTriggerDetector:
    """
    Detects social triggers in conversation context.
    """
    
    def __init__(self, conversation_manager, memory_system):
        """
        Initialize the social trigger detector.
        
        Args:
            conversation_manager: Reference to conversation management system
            memory_system: Reference to memory system
        """
        self.conversation_manager = conversation_manager
        self.memory_system = memory_system
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self):
        """
        Initialize detection patterns.
        
        Returns:
            dict: Mapping of trigger types to detection patterns
        """
        return {
            'user_mention': r'@(\w+)',
            'trend': r'\b(trending|viral|popular)\b',
            'news': r'\b(news|latest|updates)\b',
            'company': r'\b(Google|Apple|Microsoft|Twitter|X|Meta|Facebook|Amazon|Bitcoin|Ethereum|Solana)\b',
            'recommendation': r'\b(recommend|suggest|similar to)\b'
        }
    
    def detect_triggers(self, message):
        """
        Detect social triggers in a message.
        
        Args:
            message (str): User message to analyze
            
        Returns:
            list: Detected triggers with metadata
        """
        triggers = []
        
        # Check each pattern type
        for trigger_type, pattern in self.patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                for match in matches:
                    triggers.append({
                        'type': trigger_type,
                        'match': match,
                        'context': self._extract_context(message, match)
                    })
        
        return triggers
    
    def _extract_context(self, message, match):
        """
        Extract relevant context around a match.
        
        Args:
            message (str): Full message
            match (str): Matched trigger text
            
        Returns:
            str: Context surrounding the match
        """
        # Implementation would extract words around the match
        pass
    
    def prioritize_triggers(self, triggers, conversation_context):
        """
        Prioritize detected triggers based on conversation context.
        
        Args:
            triggers (list): Detected triggers
            conversation_context: Current conversation context
            
        Returns:
            list: Prioritized triggers
        """
        # Implementation would score and rank triggers
        pass
    
    def should_trigger_social_search(self, message, conversation_context):
        """
        Determine if a social search should be triggered.
        
        Args:
            message (str): User message
            conversation_context: Current conversation context
            
        Returns:
            tuple: (should_trigger, trigger_data)
        """
        triggers = self.detect_triggers(message)
        if not triggers:
            return False, None
            
        prioritized_triggers = self.prioritize_triggers(triggers, conversation_context)
        if not prioritized_triggers:
            return False, None
            
        top_trigger = prioritized_triggers[0]
        
        # Check user preferences from memory
        user_id = conversation_context.user_id
        user_preferences = self.memory_system.get_user_preferences(user_id, 'social_triggers')
        
        # If user has disabled this trigger type, don't trigger
        if user_preferences and top_trigger['type'] in user_preferences.get('disabled_triggers', []):
            return False, None
            
        return True, top_trigger
```

### 2. Nitter Service Integration
```python
class NitterService:
    """
    Service for interacting with Nitter.
    """
    
    def __init__(self, nitter_url="http://localhost:8085"):
        """
        Initialize the Nitter service.
        
        Args:
            nitter_url (str): URL of the Nitter instance
        """
        self.nitter_url = nitter_url
        self.scraper = NtScraper()
        
    def handle_social_trigger(self, trigger, conversation_context):
        """
        Handle a social trigger by retrieving appropriate data.
        
        Args:
            trigger (dict): Trigger data
            conversation_context: Current conversation context
            
        Returns:
            dict: Retrieved social data
        """
        trigger_type = trigger['type']
        match = trigger['match']
        
        if trigger_type == 'user_mention':
            # Extract username without @ symbol
            username = match.lstrip('@')
            return self.get_user_data(username)
            
        elif trigger_type == 'trend':
            # Get topic from context
            topic = self._extract_topic(trigger['context'], conversation_context)
            return self.get_trend_data(topic)
            
        elif trigger_type == 'news':
            # Get topic from context
            topic = self._extract_topic(trigger['context'], conversation_context)
            return self.get_news_data(topic)
            
        elif trigger_type == 'company':
            return self.get_company_data(match)
            
        elif trigger_type == 'recommendation':
            # Get subject from context
            subject = self._extract_subject(trigger['context'], conversation_context)
            return self.get_recommendation_data(subject)
            
        return None
        
    def get_user_data(self, username):
        """
        Get data for a specific user.
        
        Args:
            username (str): Username to retrieve data for
            
        Returns:
            dict: User data including profile and recent tweets
        """
        try:
            profile = self.scraper.get_profile_info(username, mode='simple')
            tweets = self.scraper.get_tweets(username, mode='user', limit=5)
            
            return {
                'profile': profile,
                'recent_tweets': tweets
            }
        except Exception as e:
            logging.error(f"Error retrieving user data for {username}: {e}")
            return None
            
    def get_trend_data(self, topic=None):
        """
        Get trending data, optionally filtered by topic.
        
        Args:
            topic (str, optional): Topic to filter trends by
            
        Returns:
            dict: Trending data
        """
        try:
            if topic:
                tweets = self.scraper.get_tweets(f"{topic} trending", mode='term', limit=10)
            else:
                # This would need to be implemented based on Nitter's capabilities
                tweets = self.scraper.get_tweets("trending", mode='term', limit=10)
                
            return {
                'topic': topic,
                'trending_tweets': tweets
            }
        except Exception as e:
            logging.error(f"Error retrieving trend data for {topic}: {e}")
            return None
    
    # Additional methods for other trigger types would be implemented similarly
    
    def _extract_topic(self, context, conversation_context):
        """
        Extract topic from trigger context and conversation context.
        
        Args:
            context (str): Context around the trigger
            conversation_context: Current conversation context
            
        Returns:
            str: Extracted topic
        """
        # Implementation would use NLP to extract relevant topic
        pass
        
    def _extract_subject(self, context, conversation_context):
        """
        Extract subject for recommendation from context.
        
        Args:
            context (str): Context around the trigger
            conversation_context: Current conversation context
            
        Returns:
            str: Extracted subject
        """
        # Implementation would use NLP to extract recommendation subject
        pass
```

### 3. Integration with Conversation Management
```python
class ConversationManager:
    # Existing implementation...
    
    async def process_message(self, context_id, user_id, message, message_type):
        """
        Process a message in a conversation.
        
        Args:
            context_id (str): Conversation context ID
            user_id (str): User ID
            message (str): Message content
            message_type (str): Type of message ('user' or 'assistant')
            
        Returns:
            dict: Processing result
        """
        # Existing message processing...
        
        # Check for social triggers if message is from user
        if message_type == 'user':
            should_trigger, trigger_data = self.social_trigger_detector.should_trigger_social_search(
                message, self.get_context(context_id, user_id)
            )
            
            if should_trigger:
                # Create background task for social data retrieval
                self.create_background_task(
                    context_id,
                    'social_search',
                    {
                        'trigger': trigger_data,
                        'user_id': user_id
                    }
                )
        
        # Continue with existing processing...
    
    async def execute_background_task(self, task):
        """
        Execute a background task.
        
        Args:
            task (dict): Task data
            
        Returns:
            dict: Task result
        """
        # Existing background task handling...
        
        if task['type'] == 'social_search':
            trigger = task['data']['trigger']
            user_id = task['data']['user_id']
            context_id = task['context_id']
            
            # Get conversation context
            context = self.get_context(context_id, user_id)
            
            # Retrieve social data
            social_data = self.nitter_service.handle_social_trigger(trigger, context)
            
            if social_data:
                # Store in memory system
                self.memory_system.store_social_data(user_id, trigger, social_data)
                
                # Update conversation context
                context.add_background_info('social_data', social_data)
                
                return {
                    'success': True,
                    'data': social_data
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to retrieve social data'
                }
        
        # Continue with existing task types...
```

## Integration with Grace Architecture

### 1. Memory System Integration
- **Storage**: Social trigger patterns and preferences stored in memory system
- **Retrieval**: Memory system provides context for trigger detection
- **Learning**: Memory system tracks effectiveness of triggers for improvement

### 2. Conversation Management Integration
- **Trigger Detection**: Integrated into message processing pipeline
- **Background Tasks**: Social searches run as background tasks
- **Context Enhancement**: Social data enhances conversation context

### 3. API Integration
- **Nitter Service**: Direct integration with Nitter API functions
- **Data Flow**: Social data flows through API integration layer
- **Response Formatting**: API responses formatted for conversation use

## User Experience Considerations

### 1. Transparency
- **Indication**: Subtle indication when social search is triggered
- **Attribution**: Clear attribution of information to social sources
- **Control**: User ability to enable/disable specific trigger types

### 2. Relevance
- **Contextual**: Social information presented in context
- **Timely**: Information provided at appropriate conversation points
- **Valuable**: Focus on high-quality, relevant social data

### 3. Privacy
- **Consent**: User awareness of social data collection
- **Data Handling**: Appropriate handling of potentially sensitive information
- **Retention**: Clear policies on social data retention

## Performance Considerations

### 1. Efficiency
- **Lightweight Detection**: Efficient pattern matching to minimize overhead
- **Selective Triggering**: Only trigger when high confidence of relevance
- **Caching**: Cache common social queries to reduce API calls

### 2. Reliability
- **Error Handling**: Graceful handling of Nitter service failures
- **Fallbacks**: Alternative data sources when social data unavailable
- **Degradation**: Gradual feature degradation rather than complete failure

## Future Enhancements

### 1. Advanced Trigger Detection
- **Sentiment Analysis**: Detect emotional context for more relevant social data
- **Multi-turn Analysis**: Consider conversation history for trigger detection
- **Implicit Triggers**: Recognize implied needs for social information

### 2. Expanded Social Sources
- **Additional Platforms**: Integration with other social media platforms
- **Cross-platform Analysis**: Compare information across platforms
- **Verification**: Cross-reference information for accuracy

### 3. Personalization
- **Learning Preferences**: Adapt trigger sensitivity to user preferences
- **Interest Profiling**: Build profiles of user interests for better targeting
- **Proactive Suggestions**: Suggest social information before explicitly asked
