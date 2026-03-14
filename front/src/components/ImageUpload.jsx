import React, { useState } from 'react';
import { Upload, Trash2, Image } from 'lucide-react';

// Компонент для загрузки изображений через Drag & Drop
const ImageUpload = ({ images, onImagesChange }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const newImage = {
            id: Date.now() + Math.random(),
            name: file.name,
            url: e.target.result
          };
          onImagesChange([...images, newImage]);
        };
        reader.readAsDataURL(file);
      }
    });
  };

  const removeImage = (id) => {
    onImagesChange(images.filter(img => img.id !== id));
  };

  return (
    <div className="bg-[#21262F] rounded-lg p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-[#FFFB78] mb-6 border-b border-[#646C89] pb-3">
        Загрузка изображений сварных швов
      </h2>
      
      {/* Drag & Drop зона */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-10 text-center transition-all
          ${dragActive 
            ? 'border-[#0084FF] bg-[#0084FF]/10' 
            : 'border-[#646C89] hover:border-[#0084FF]/50'
          }
        `}
      >
        <Upload size={48} className="mx-auto mb-4 text-[#646C89]" />
        <p className="text-lg mb-2 text-white">
          Перетащите изображения сюда
        </p>
        <p className="text-[#646C89] mb-4">или</p>
        <label className="inline-block bg-[#0084FF] hover:bg-[#0084FF]/80 text-white px-6 py-3 rounded-lg cursor-pointer transition-colors">
          Выбрать файлы
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
      </div>

      {/* Превью загруженных изображений */}
      {images.length > 0 && (
        <div className="mt-6">
          <h3 className="text-md font-medium mb-4 text-white flex items-center gap-2">
            <Image size={20} />
            Загруженные изображения ({images.length})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {images.map((img) => (
              <div key={img.id} className="relative group">
                <img
                  src={img.url}
                  alt={img.name}
                  className="w-full h-32 object-cover rounded-lg border border-[#646C89]"
                />
                <button
                  onClick={() => removeImage(img.id)}
                  className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 size={16} />
                </button>
                <p className="text-xs text-[#646C89] mt-2 truncate">
                  {img.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
