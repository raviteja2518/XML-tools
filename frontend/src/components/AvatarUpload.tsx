"use client";

import React, { useState } from "react";
import api from "@/utils/api";
import { useAuth } from "@/context/AuthContext";
import { Camera, Loader2 } from "lucide-react";

interface AvatarUploadProps {
  currentAvatar?: string;
}

const AvatarUpload: React.FC<AvatarUploadProps> = ({ currentAvatar }) => {
  const { updateUser, token } = useAuth();
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/profile/upload-picture", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      updateUser(response.data);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload profile picture.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="relative group w-32 h-32 mx-auto">
      <div className="w-full h-full rounded-full overflow-hidden border-4 border-indigo-500/30 bg-gray-800 flex items-center justify-center">
        {currentAvatar ? (
          <img
            src={`${process.env.NEXT_PUBLIC_API_URL?.replace("/api", "")}${currentAvatar}`}
            alt="Profile"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-gray-500 text-4xl font-bold uppercase">
            {/* Fallback to initial if no avatar */}
          </div>
        )}
      </div>

      <label className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer rounded-full">
        {uploading ? (
          <Loader2 className="w-8 h-8 text-white animate-spin" />
        ) : (
          <Camera className="w-8 h-8 text-white" />
        )}
        <input
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
      </label>
    </div>
  );
};

export default AvatarUpload;
