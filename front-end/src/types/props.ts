import React from "react";

export interface IPaginationProps {
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
    currentPage: number;
}