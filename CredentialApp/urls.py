from django.urls import path
from . import views

urlpatterns = [

    #  ************ COMMON URLS **************
    path('',views.index,name='index'),   # for loading index page
    path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/', views.logout, name='logout'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('verify_forgot_otp/', views.verify_forgot_otp, name='verify_forgot_otp'),
    path('new_password/', views.new_password, name='new_password'),

    #  *********** ORPHANAGE MODULE URLS ************
    path('Orphanage_Home',views.Orphanage_Home,name='Orphanage_Home'),
    path('orphanage_verification',views.orphanage_verification,name='orphanage_verification'),
    path('O_Profile/', views.O_Profile, name='O_Profile'),
    path('O_Profile_edit/', views.O_Profile_edit, name='O_Profile_edit'),
    path('change_password',views.change_password,name='change_password'),
    path('children_add',views.children_add,name='children_add'),
    path('children_list',views.children_list,name='children_list'),
    path('children_details/<int:id>/',views.children_details,name='children_details'),
    path('delete_education/<int:id>/',views.delete_education,name='delete_education'),
    path('delete_children/<int:id>/',views.delete_children,name='delete_children'),
    path('volunteer_list',views.volunteer_list,name='volunteer_list'),
    path('Accept_Volunteer_Request/<int:id>/',views.Accept_Volunteer_Request,name='Accept_Volunteer_Request'),
    path('delete_volunteer/<int:id>/',views.delete_volunteer,name='delete_volunteer'),
    path('load-orphanages/', views.load_orphanages, name='ajax_load_orphanages'),
    path('volunteer_details/<int:id>/',views.volunteer_details,name='volunteer_details'),
    path('Add_Donation/',views.Add_Donation,name='Add_Donation'),
    path('Add_Data/',views.Add_Data,name='Add_Data'),
    path('View_Item/',views.View_Item,name='View_Item'),
    path('View_Data/',views.View_Data,name='View_Data'),
    path('delete_Item/<int:id>/',views.delete_Item,name='delete_Item'),
    path('delete_data/<int:id>/',views.delete_data,name='delete_data'),
    path('payment_done/',views.payment_done,name='payment_done'),
    path('View_amount/',views.View_amount,name='View_amount'),
    path('download_donations_csv/',views.download_donations_csv,name='download_donations_csv'),
    path('Delete_orphanage/<int:id>/',views.Delete_orphanage,name='Delete_orphanage'),
    path('D_View_amount/',views.D_View_amount,name='D_View_amount'),
    path('download_data_csv/',views.download_data_csv,name='download_data_csv'),
    path('upload_marks/',views.upload_marks,name='upload_marks'),
    path('plot_graphs/<int:id>/', views.plot_graphs, name='plot_graphs'),
    path('view_donation_item/', views.view_donation_item, name='view_donation_item'),
    path('leave_list/', views.leave_list, name='leave_list'),
    path('Accept_leaves/<int:id>/', views.Accept_leaves, name='Accept_leaves'),  # volunteer accept donations
    path('assign_volunteer/<int:donation_id>/', views.assign_volunteer, name='assign_volunteer'),  # volunteer accept donations
    path('orphanage_Accept_Volunteer_donations/<int:id>/', views.orphanage_Accept_Volunteer_donations, name='orphanage_Accept_Volunteer_donations'),  # orphanage accept donations
    path('add_category/', views.add_category, name='add_category'),
    path('View_category/', views.View_category, name='View_category'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),
    path('leave-requests/<int:volunteer_id>/', views.leave_requests, name='leave_requests'),
    path('approve_leave/<int:volunteer_id>/', views.approve_leave, name='approve_leave'),
    path('download_donations_pdf/', views.download_donations_pdf, name='download_donations_pdf'),


    #  **************** VOLUNTEER MODULE URLS **********************
    path('Volunteer_Home',views.Volunteer_Home,name='Volunteer_Home'),  # for loading volunteer home page
    path('volunteer_verification',views.volunteer_verification,name='volunteer_verification'),  # for loading volunteer verification page
    path('V_Profile/', views.V_Profile, name='V_Profile'),  # for loading volunteer profile page
    path('V_Profile_edit/', views.V_Profile_edit, name='V_Profile_edit'),  # volunteer profile editing function 
    path('volunteer_viewdonation/', views.volunteer_viewdonation, name='volunteer_viewdonation'),  # volunteer profile editing function 
    path('Accept_Volunteer_donations/<int:id>/', views.Accept_Volunteer_donations, name='Accept_Volunteer_donations'),  # volunteer accept donations
    path('apply_leave/', views.apply_leave, name='apply_leave'),  # volunteer applying leave 
    path('volunteer_view_leaves/', views.volunteer_view_leaves, name='volunteer_view_leaves'),  # volunteer view leave 
    path('delete_leave/<int:id>/', views.delete_leave, name='delete_leave'),  # volunteer applying leave 
    path('volunteer_change_password',views.volunteer_change_password,name='volunteer_change_password'),


    #  **************** Donor MODULE URLS **********************
    path('Donor_Home',views.Donor_Home,name='Donor_Home'),  # for loading donor home page
    path('D_Profile/', views.D_Profile, name='D_Profile'),  # for loading Donor profile page
    path('addnew_address/', views.addnew_address, name='addnew_address'),  # for loading Donor profile page
    path('D_newaddress_view/', views.D_newaddress_view, name='D_newaddress_view'),  # for loading Donor new address page
    path('donor_change_password/', views.donor_change_password, name='donor_change_password'),  #  Donor change password 
    path('Donor_details/', views.Donor_details, name='Donor_details'),  #  Donor Details Add 
    path('Delete_details/<int:id>/', views.Delete_details, name='Delete_details'),  #  Donor Details Add
    path('selectdistrict/', views.selectdistrict, name='selectdistrict'),  #  Select District to choose orphanage
    path('orphanage_details/', views.orphanage_details, name='orphanage_details'),  #  Donor view of selected orphanage
    path('selectdistrict_items',views.selectdistrict_items,name='selectdistrict_items'),
    path('load-orphanages/', views.load_orphanages, name='ajax_load_orphanages'),
    path('orphanage_details_items/', views.orphanage_details_items, name='orphanage_details_items'),
    path('load-orphanages_items/', views.load_orphanages_items, name='ajax_load_orphanages_items'),
    path('donate_items/<int:id>/', views.donate_items, name='donate_items'),
    path('donation_items_save/', views.donation_items_save, name='donation_items_save'),
    path('donation-graph/', views.donation_graph, name='donation-graph'),
    path('donor_viewdonations/', views.donor_viewdonations, name='donor_viewdonations'),

# *********************************************
    path('donation_analysys/', views.donation_analysys, name='donation_analysys'),
    path('orpanage_donation_analysys/', views.orpanage_donation_analysys, name='orpanage_donation_analysys'),

]