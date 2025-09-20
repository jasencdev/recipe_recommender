import api from './api';

export interface ParsedIngredient {
  original: string;
  quantity: number;
  unit: string;
  name: string;
  preparation?: string;
}

export interface EnrichedIngredients {
  recipeId: string;
  originalIngredients: string[];
  detailedIngredients: string[];
  parsedIngredients: ParsedIngredient[];
}

// Parse ingredient string to extract quantity, unit, and name
export function parseIngredient(ingredientStr: string): ParsedIngredient {
  // Remove leading/trailing whitespace
  const trimmed = ingredientStr.trim();

  // Regex to match quantity, unit, and ingredient name
  // Matches patterns like: "1 cup flour", "1/2 teaspoon salt", "2 tablespoons olive oil"
  const match = trimmed.match(/^(\d+(?:\/\d+)?(?:\.\d+)?)\s*(\w+)?\s+(.+)$/);

  if (match) {
    const [, quantityStr, unit, name] = match;

    // Parse fractional quantities like "1/2"
    let quantity: number;
    if (quantityStr.includes('/')) {
      const [num, den] = quantityStr.split('/').map(Number);
      quantity = num / den;
    } else {
      quantity = parseFloat(quantityStr);
    }

    // Extract preparation instructions (text in parentheses)
    const preparationMatch = name.match(/^(.+?)\s*\((.+)\)$/);
    const cleanName = preparationMatch ? preparationMatch[1].trim() : name.trim();
    const preparation = preparationMatch ? preparationMatch[2].trim() : undefined;

    return {
      original: trimmed,
      quantity,
      unit: unit || '',
      name: cleanName,
      preparation
    };
  }

  // If no match, treat as name-only ingredient
  return {
    original: trimmed,
    quantity: 1,
    unit: '',
    name: trimmed,
  };
}

// Scale ingredient quantities based on serving size multiplier
export function scaleIngredient(ingredient: ParsedIngredient, multiplier: number): ParsedIngredient {
  return {
    ...ingredient,
    quantity: ingredient.quantity * multiplier,
  };
}

// Format scaled ingredient back to readable string
export function formatIngredient(ingredient: ParsedIngredient): string {
  const { quantity, unit, name, preparation } = ingredient;

  // Format quantity (handle fractions nicely)
  let quantityStr: string;
  if (quantity === 0) {
    quantityStr = '0';
  } else if (quantity % 1 === 0) {
    quantityStr = quantity.toString();
  } else if (quantity < 1) {
    // Try to display as fraction for common values
    if (Math.abs(quantity - 0.5) < 0.01) quantityStr = '1/2';
    else if (Math.abs(quantity - 0.25) < 0.01) quantityStr = '1/4';
    else if (Math.abs(quantity - 0.75) < 0.01) quantityStr = '3/4';
    else if (Math.abs(quantity - 0.33) < 0.01) quantityStr = '1/3';
    else if (Math.abs(quantity - 0.67) < 0.01) quantityStr = '2/3';
    else if (Math.abs(quantity - 0.125) < 0.01) quantityStr = '1/8';
    else quantityStr = quantity.toFixed(2).replace(/\.?0+$/, '');
  } else {
    // For quantities > 1, show one decimal if needed
    quantityStr = quantity % 1 === 0 ? quantity.toString() : quantity.toFixed(1);
  }

  // Build the formatted string with better spacing
  let formatted = '';

  // Add quantity and unit if they exist
  if (quantityStr !== '1' || unit) {
    formatted = quantityStr;
    if (unit) formatted += ` ${unit}`;
    formatted += ' ';
  }

  formatted += name;

  return formatted;
}

// Get enriched ingredients for a recipe from the model data
export async function getEnrichedIngredients(recipeId: string): Promise<EnrichedIngredients | null> {
  try {
    const response = await api.get(`/recipes/${recipeId}/enriched-ingredients`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch enriched ingredients:', error);
    return null;
  }
}

// Scale all ingredients in a recipe by serving multiplier
export function scaleRecipeIngredients(
  enrichedIngredients: EnrichedIngredients,
  servingMultiplier: number
): ParsedIngredient[] {
  return enrichedIngredients.parsedIngredients.map(ingredient =>
    scaleIngredient(ingredient, servingMultiplier)
  );
}