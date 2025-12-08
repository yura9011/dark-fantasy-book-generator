const API_URL = 'http://localhost:8000';

export const generateBook = async (data) => {
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                book_title: String(data.book_title || data.title || "Untitled"),
                num_chapters: parseInt(data.num_chapters || data.chapters || 3),
                num_subchapters: 2,
                plot: String(data.plot || ""),
                keywords: data.themes || [],
                existing_state: data.existingState || {},
                stop_after: data.stopAfter || null,
                inquiry_responses: data.inquiry_responses || {}
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Validation Error:', JSON.stringify(errorData, null, 2));
            const errorMessage = errorData.detail
                ? JSON.stringify(errorData.detail)
                : (errorData.error || 'Failed to generate book');
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
