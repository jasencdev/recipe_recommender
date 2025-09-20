import { useState, useEffect } from 'react';
import { Button } from './button';
import { isRecipeSaved, toggleSaveRecipe } from '../services/api';

interface SaveButtonProps {
    recipeId: string;
    size?: 'sm' | 'md' | 'lg';
    color?: 'default' | 'gray' | 'red';
    className?: string;
    onSaveChange?: (isSaved: boolean) => void;
    onClick?: (e: React.MouseEvent) => void;
}

export default function SaveButton({
    recipeId,
    size = 'sm',
    color = 'gray',
    className = '',
    onSaveChange,
    onClick
}: SaveButtonProps) {
    const [isSaved, setIsSaved] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isToggling, setIsToggling] = useState(false);

    useEffect(() => {
        const checkSaveStatus = async () => {
            try {
                setIsLoading(true);
                const saved = await isRecipeSaved(recipeId);
                setIsSaved(saved);
            } catch (error) {
                console.error('Failed to check save status:', error);
            } finally {
                setIsLoading(false);
            }
        };

        checkSaveStatus();
    }, [recipeId]);

    const handleToggle = async (e: React.MouseEvent) => {
        // Stop event propagation to prevent card click
        e.stopPropagation();

        // Call the custom onClick handler if provided
        onClick?.(e);

        try {
            setIsToggling(true);
            const newSavedState = await toggleSaveRecipe(recipeId);
            setIsSaved(newSavedState);
            onSaveChange?.(newSavedState);
        } catch (error) {
            console.error('Failed to toggle save state:', error);
        } finally {
            setIsToggling(false);
        }
    };

    if (isLoading) {
        return (
            <Button size={size} color={color} disabled className={className}>
                ...
            </Button>
        );
    }

    return (
        <Button
            size={size}
            color={isSaved ? 'red' : color}
            onClick={handleToggle}
            disabled={isToggling}
            className={`flex items-center gap-1 ${className}`}
        >
            {isSaved ? (
                <>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                    </svg>
                    {isToggling ? 'Removing...' : 'Saved'}
                </>
            ) : (
                <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    {isToggling ? 'Saving...' : 'Save'}
                </>
            )}
        </Button>
    );
}