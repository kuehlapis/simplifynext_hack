import React, { Dispatch, SetStateAction } from "react";

interface EmailModalProps {
  userName: string;
  setUserName: Dispatch<SetStateAction<string>>;
  userEmail: string;
  setUserEmail: Dispatch<SetStateAction<string>>;
  onSubmit: () => void;
  onClose: () => void;
}

const EmailModal: React.FC<EmailModalProps> = ({
  userName,
  setUserName,
  userEmail,
  setUserEmail,
  onSubmit,
  onClose
}) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full shadow-lg">
        <h2 className="text-xl font-bold mb-4">Enter your details</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Your Name"
            className="w-full border px-3 py-2 rounded"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
          />
          <input
            type="email"
            placeholder="Your Email"
            className="w-full border px-3 py-2 rounded"
            value={userEmail}
            onChange={(e) => setUserEmail(e.target.value)}
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              onClick={onSubmit}
              className="px-4 py-2 bg-primary text-white rounded hover:opacity-90"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailModal;
