"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Product {
  id: number;
  title: string;
  price: number;
  category?: string;
  image?: string;
  description?: string;
}

interface ProductCardsProps {
  products: Product[];
}

export default function ProductCards({ products }: ProductCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
      {products.map((product) => (
        <Card
          key={product.id}
          className="overflow-hidden hover:shadow-md transition-shadow flex flex-col bg-white border border-gray-200"
        >
          <div className="flex flex-col h-full p-3 sm:p-4">
            {/* Product Image - larger on mobile */}
            {product.image && (
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-40 sm:h-32 object-cover rounded-lg mb-3 flex-shrink-0"
              />
            )}

            {/* Product Title */}
            <h3 className="font-semibold text-sm sm:text-base line-clamp-2 mb-2 flex-grow">
              {product.title}
            </h3>

            {/* Category Badge */}
            {product.category && (
              <p className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded mb-2 w-fit">
                {product.category}
              </p>
            )}

            {/* Price - prominent */}
            <p className="text-xl sm:text-lg font-bold text-blue-600 mb-2">
              ${product.price.toFixed(2)}
            </p>

            {/* Description */}
            {product.description && (
              <p className="text-xs sm:text-sm text-gray-600 line-clamp-2 mb-3 flex-grow">
                {product.description}
              </p>
            )}

            {/* Action Buttons - full width, tap-friendly */}
            <div className="flex flex-col gap-2 mt-auto">
              <Button
                size="sm"
                variant="default"
                className="w-full text-sm sm:text-base h-10 sm:h-9 font-medium"
                onClick={() => {
                  const message = `Add ${product.title} to my cart`;
                  console.log("Requested:", message);
                }}
              >
                Add to Cart
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="w-full text-sm sm:text-base h-10 sm:h-9 font-medium"
                onClick={() => {
                  const message = `Tell me more about ${product.title}`;
                  console.log("Requested:", message);
                }}
              >
                Details
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
