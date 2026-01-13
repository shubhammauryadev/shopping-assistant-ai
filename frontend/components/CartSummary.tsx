"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface CartItem {
  product_id: number;
  product_title: string;
  price: number;
  quantity: number;
}

interface CartData {
  items: CartItem[];
  total_items?: number;
  total_price?: number;
}

interface CartSummaryProps {
  cart: CartData;
  onClearCart?: () => void;
}

export default function CartSummary({ cart, onClearCart }: CartSummaryProps) {
  // Calculate totals from items as fallback if backend totals are missing or 0
  const calculatedTotalItems = cart.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
  const calculatedTotalPrice = cart.items.reduce((sum, item) => {
    const itemPrice = item.price || 0;
    const itemQuantity = item.quantity || 0;
    return sum + (itemPrice * itemQuantity);
  }, 0);

  // Use backend totals if available, otherwise use calculated values
  const displayTotalItems = cart.total_items !== undefined && cart.total_items !== 0 ? cart.total_items : calculatedTotalItems;
  const displayTotalPrice = cart.total_price !== undefined && cart.total_price !== 0 ? cart.total_price : calculatedTotalPrice;

  return (
    <Card className="bg-gradient-to-br from-blue-50 to-gray-50 border border-blue-100">
      {/* Cart Header */}
      <div className="px-4 py-3 sm:px-4 sm:py-4 border-b border-blue-100">
        <h3 className="font-bold text-base sm:text-lg text-gray-900">🛒 Shopping Cart</h3>
      </div>

      {/* Cart Content */}
      {cart.items.length === 0 ? (
        <div className="px-4 py-6 text-center">
          <p className="text-gray-500 text-sm">Your cart is empty</p>
        </div>
      ) : (
        <div className="divide-y divide-blue-100">
          {/* Cart Items */}
          <div className="space-y-0 px-4 py-3 sm:py-4">
            {cart.items.map((item) => (
              <div
                key={item.product_id}
                className="flex justify-between items-start py-3 first:pt-0 last:pb-0"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm sm:text-base text-gray-900 line-clamp-2 mb-1">
                    {item.product_title}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600">
                    {item.quantity} × ${item.price !== undefined ? item.price.toFixed(2) : "..."}
                  </p>
                </div>
                <p className="font-bold text-sm sm:text-base text-blue-600 ml-3 flex-shrink-0">
                  ${item.price !== undefined ? (item.quantity * item.price).toFixed(2) : "..."}
                </p>
              </div>
            ))}
          </div>

          {/* Cart Total */}
          <div className="px-4 py-3 sm:py-4 bg-white">
            <div className="flex justify-between items-center mb-3">
              <span className="font-semibold text-gray-900 text-sm sm:text-base">
                Total ({displayTotalItems} item{displayTotalItems !== 1 ? "s" : ""}):
              </span>
              <span className="font-bold text-lg sm:text-xl text-blue-600">
                ${displayTotalPrice.toFixed(2)}
              </span>
            </div>

            {/* Clear Cart Button */}
            {onClearCart && displayTotalItems > 0 && (
              <Button
                onClick={onClearCart}
                variant="outline"
                className="w-full text-sm text-red-600 border-red-200 hover:bg-red-50"
              >
                🗑️ Clear Cart
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
