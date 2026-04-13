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

  const HR_ROLES = [
    "acadadmin",
    "studentacadadmin",
    "Professor",
    "Assistant Professor",
    "Associate Professor",
    "HOD",
    "Dean Academic",
  ];
  const tabItems = [
    { title: "Leave", path: "/hr2/leave", roles: HR_ROLES },
    { title: "Leave Inbox", path: "/hr2/leave-inbox", roles: HR_ROLES },
    { title: "LTC", path: "/hr2/ltc", roles: HR_ROLES },
    { title: "CPDA Advance", path: "/hr2/cpda-advance", roles: HR_ROLES },
    {
      title: "CPDA Reimbursement",
      path: "/hr2/cpda-reimbursement",
      roles: HR_ROLES,
    },
    { title: "Appraisal", path: "/hr2/appraisal", roles: HR_ROLES },
    {
      title: "Workflow Actions",
      path: "/hr2/workflow-actions",
      roles: HR_ROLES,
    },
  ];

  const filteredTabs = tabItems.filter((tab) => tab.roles.includes(userRole));

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
