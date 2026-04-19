import React, { useRef } from "react";
import { NavLink } from "react-router-dom";
import { CaretCircleLeft, CaretCircleRight } from "phosphor-react";
import { useSelector } from "react-redux";

export default function Nav() {
  const scrollContainerRef = useRef(null);
  const userRole = useSelector((state) => state.user.role);

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -150, behavior: "smooth" });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 150, behavior: "smooth" });
    }
  };

  const activeLinkStyle = {
    backgroundColor: "#15abff13",
    color: "#15abff",
    borderBottom: "2px solid #15abff",
    borderBottomLeftRadius: "4px",
    borderBottomRightRadius: "4px",
  };

  const defaultLinkStyle = {
    textDecoration: "none",
    padding: "10px 15px",
    color: "black",
    display: "block",
    width: "100%",
    textAlign: "center",
    borderBottom: "2px solid #e0e0e0",
  };

  // All roles that can access HR2
  const HR_ROLES = [
    "faculty", "staff", "Professor", "Assistant Professor", "Associate Professor",
    "Employee", "Dean Academic", "acadadmin", "studentacadadmin",
    "HOD", "Director", "Registrar", "HR Admin", "HR Administrator",
    "Accountant", "Finance",
  ];

  // Roles that submit forms
  const APPLY_ROLES = [
    "faculty", "staff", "Professor", "Assistant Professor", "Associate Professor",
    "Employee", "Dean Academic", "HOD", "acadadmin", "studentacadadmin",
  ];

  // Roles that approve (have an inbox)
  const APPROVAL_ROLES = [
    "HOD", "Director", "Registrar", "HR Admin", "HR Administrator",
    "Accountant", "Finance",
  ];

  const canApply = APPLY_ROLES.includes(userRole);
  const canApprove = APPROVAL_ROLES.includes(userRole);

  const tabItems = [
    // Employee/Faculty-only tabs
    { title: "Leave", path: "/hr2/leave", show: canApply },
    { title: "Leave Inbox", path: "/hr2/leave-inbox", show: canApprove },
    // Shared module tabs (everyone with HR access sees them, Inbox/Apply within handled per-role)
    { title: "LTC", path: "/hr2/ltc", show: true },
    { title: "CPDA Advance", path: "/hr2/cpda-advance", show: true },
    { title: "CPDA Reimbursement", path: "/hr2/cpda-reimbursement", show: true },
    { title: "Appraisal", path: "/hr2/appraisal", show: true },
    { title: "Workflow Actions", path: "/hr2/workflow-actions", show: canApply },
  ];

  const filteredTabs = tabItems.filter(
    (tab) => HR_ROLES.includes(userRole) && tab.show,
  );

  if (filteredTabs.length === 0) return null;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        height: "5vh",
        marginBottom: "30px",
      }}
    >
      <button
        style={{ background: "transparent", border: "none", cursor: "pointer" }}
        onClick={scrollLeft}
      >
        <CaretCircleLeft size={25} />
      </button>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          overflowX: "auto",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          flexWrap: "nowrap",
        }}
        ref={scrollContainerRef}
      >
        {filteredTabs.map((tab, index) => (
          <div
            key={index}
            style={{ display: "flex", alignItems: "center", padding: "0" }}
          >
            <NavLink
              to={tab.path}
              style={({ isActive }) => ({
                ...defaultLinkStyle,
                ...(isActive ? activeLinkStyle : {}),
              })}
            >
              {tab.title}
            </NavLink>
          </div>
        ))}
      </div>
      <button
        style={{ background: "transparent", border: "none", cursor: "pointer" }}
        onClick={scrollRight}
      >
        <CaretCircleRight size={25} />
      </button>
    </div>
  );
}
