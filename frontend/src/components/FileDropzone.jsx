import { useRef } from "react";

export default function FileDropzone({ file, onFileChange }) {
  const inputRef = useRef(null);

  const onDrop = (event) => {
    event.preventDefault();
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) onFileChange(dropped);
  };

  return (
    <div
      className="dropzone"
      onDragOver={(event) => event.preventDefault()}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        hidden
        onChange={(event) => onFileChange(event.target.files?.[0])}
      />
      <p>{file ? `Selected: ${file.name}` : "Drop file here or click to choose"}</p>
    </div>
  );
}
